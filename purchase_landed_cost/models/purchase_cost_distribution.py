# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, exceptions, api, _
import openerp.addons.decimal_precision as dp


class PurchaseCostDistribution(models.Model):
    _name = "purchase.cost.distribution"
    _description = "Purchase landed costs distribution"
    _order = 'name desc'

    @api.one
    @api.depends('total_expense', 'total_purchase')
    def _compute_amount_total(self):
        self.amount_total = self.total_purchase + self.total_expense

    @api.one
    @api.depends('cost_lines', 'cost_lines.total_amount')
    def _compute_total_purchase(self):
        self.total_purchase = sum([x.total_amount for x in self.cost_lines])

    @api.one
    @api.depends('cost_lines', 'cost_lines.product_price_unit')
    def _compute_total_price_unit(self):
        self.total_price_unit = sum([x.product_price_unit for x in
                                     self.cost_lines])

    @api.one
    @api.depends('cost_lines', 'cost_lines.product_qty')
    def _compute_total_uom_qty(self):
        self.total_uom_qty = sum([x.product_qty for x in self.cost_lines])

    @api.one
    @api.depends('cost_lines', 'cost_lines.total_weight')
    def _compute_total_weight(self):
        self.total_weight = sum([x.total_weight for x in self.cost_lines])

    @api.one
    @api.depends('cost_lines', 'cost_lines.total_weight_net')
    def _compute_total_weight_net(self):
        self.total_weight_net = sum([x.total_weight_net for x in
                                     self.cost_lines])

    @api.one
    @api.depends('cost_lines', 'cost_lines.total_volume')
    def _compute_total_volume(self):
        self.total_volume = sum([x.total_volume for x in self.cost_lines])

    @api.one
    @api.depends('expense_lines', 'expense_lines.expense_amount')
    def _compute_total_expense(self):
        self.total_expense = sum([x.expense_amount for x in
                                  self.expense_lines])

    def _expense_lines_default(self):
        expenses = self.env['purchase.expense.type'].search(
            [('default_expense', '=', True)])
        return [{'type': x, 'expense_amount': x.default_amount}
                for x in expenses]

    name = fields.Char(string='Distribution number', required=True,
                       select=True, default='/')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=(lambda self: self.env['res.company']._company_default_get(
            'purchase.cost.distribution')))
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency',
        related="company_id.currency_id")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('calculated', 'Calculated'),
         ('done', 'Done'),
         ('error', 'Error'),
         ('cancel', 'Cancel')], string='Status', readonly=True,
        default='draft')
    cost_update_type = fields.Selection(
        [('direct', 'Direct Update')], string='Cost Update Type',
        default='direct', required=True)
    date = fields.Date(
        string='Date', required=True, readonly=True, select=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today)
    total_uom_qty = fields.Float(
        compute=_compute_total_uom_qty, readonly=True,
        digits_compute=dp.get_precision('Product UoS'),
        string='Total quantity')
    total_weight = fields.Float(
        compute=_compute_total_weight, string='Total gross weight',
        readonly=True,
        digits_compute=dp.get_precision('Stock Weight'))
    total_weight_net = fields.Float(
        compute=_compute_total_weight_net,
        digits_compute=dp.get_precision('Stock Weight'),
        string='Total net weight', readonly=True)
    total_volume = fields.Float(
        compute=_compute_total_volume, string='Total volume', readonly=True)
    total_purchase = fields.Float(
        compute=_compute_total_purchase,
        digits_compute=dp.get_precision('Account'), string='Total purchase')
    total_price_unit = fields.Float(
        compute=_compute_total_price_unit, string='Total price unit',
        digits_compute=dp.get_precision('Product Price'))
    amount_total = fields.Float(
        compute=_compute_amount_total,
        digits_compute=dp.get_precision('Account'), string='Total')
    total_expense = fields.Float(
        compute=_compute_total_expense,
        digits_compute=dp.get_precision('Account'), string='Total expenses')
    note = fields.Text(string='Documentation for this order')
    cost_lines = fields.One2many(
        comodel_name='purchase.cost.distribution.line', ondelete="cascade",
        inverse_name='distribution', string='Distribution lines')
    expense_lines = fields.One2many(
        comodel_name='purchase.cost.distribution.expense', ondelete="cascade",
        inverse_name='distribution', string='Expenses',
        default=_expense_lines_default)

    @api.multi
    def unlink(self):
        for c in self:
            if c.state not in ('draft', 'calculated'):
                raise exceptions.Warning(
                    _("You can't delete a confirmed cost distribution"))
        return super(PurchaseCostDistribution, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'purchase.cost.distribution')
        return super(PurchaseCostDistribution, self).create(vals)

    @api.model
    def _prepare_expense_line(self, expense_line, cost_line):
        distribution = cost_line.distribution
        if expense_line.type.calculation_method == 'amount':
            multiplier = cost_line.total_amount
            if expense_line.affected_lines:
                divisor = sum([x.total_amount for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_purchase
        elif expense_line.type.calculation_method == 'price':
            multiplier = cost_line.product_price_unit
            if expense_line.affected_lines:
                divisor = sum([x.product_price_unit for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_price_unit
        elif expense_line.type.calculation_method == 'qty':
            multiplier = cost_line.product_qty
            if expense_line.affected_lines:
                divisor = sum([x.product_qty for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_uom_qty
        elif expense_line.type.calculation_method == 'weight':
            multiplier = cost_line.total_weight
            if expense_line.affected_lines:
                divisor = sum([x.total_weight for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_weight
        elif expense_line.type.calculation_method == 'weight_net':
            multiplier = cost_line.total_weight_net
            if expense_line.affected_lines:
                divisor = sum([x.total_weight_net for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_weight_net
        elif expense_line.type.calculation_method == 'volume':
            multiplier = cost_line.total_volume
            if expense_line.affected_lines:
                divisor = sum([x.total_volume for x in
                               expense_line.affected_lines])
            else:
                divisor = distribution.total_volume
        elif expense_line.type.calculation_method == 'equal':
            multiplier = 1
            divisor = (len(expense_line.affected_lines) or
                       len(distribution.cost_lines))
        else:
            raise exceptions.Warning(
                _('No valid distribution type.'))
        if divisor:
            expense_amount = (expense_line.expense_amount * multiplier /
                              divisor)
        else:
            raise exceptions.Warning(
                _("The cost for the line '%s' can't be "
                  "distributed because the calculation method "
                  "doesn't provide valid data" % cost_line.type.name))
        return {
            'distribution_expense': expense_line.id,
            'expense_amount':       expense_amount,
            'cost_ratio':           expense_amount / cost_line.product_qty,
        }

    @api.multi
    def action_calculate(self):
        for distribution in self:
            # Check expense lines for amount 0
            if any([not x.expense_amount for x in distribution.expense_lines]):
                raise exceptions.Warning(
                    _('Please enter an amount for all the expenses'))
            # Check if exist lines in distribution
            if not distribution.cost_lines:
                raise exceptions.Warning(
                    _('There is no picking lines in the distribution'))
            # Calculating expense line
            for cost_line in distribution.cost_lines:
                cost_line.expense_lines.unlink()
                expense_lines = []
                for expense in distribution.expense_lines:
                    if (expense.affected_lines and
                            cost_line not in expense.affected_lines):
                        continue
                    expense_lines.append(
                        self._prepare_expense_line(expense, cost_line))
                cost_line.expense_lines = [(0, 0, x) for x in expense_lines]
            distribution.state = 'calculated'
        return True

    def _product_price_update(self, move, new_price):
        """Method that mimicks stock.move's product_price_update_before_done
        method behaviour, but taking into account that calculations are made
        on an already done move, and prices sources are given as parameters.
        """
        if (move.location_id.usage == 'supplier' and
                move.product_id.cost_method == 'average'):
            product = move.product_id
            qty_available = product.product_tmpl_id.qty_available
            product_avail = qty_available - move.product_qty
            if product_avail <= 0:
                new_std_price = new_price
            else:
                domain_quant = [
                    ('product_id', 'in',
                     product.product_tmpl_id.product_variant_ids.ids),
                    ('id', 'not in', move.quant_ids.ids)]
                quants = self.env['stock.quant'].read_group(
                    domain_quant, ['product_id', 'qty', 'cost'], [])[0]
                # Get the standard price
                new_std_price = ((quants['cost'] * quants['qty'] +
                                  new_price * move.product_qty) /
                                 qty_available)
            # Write the standard price, as SUPERUSER_ID, because a
            # warehouse manager may not have the right to write on products
            product.sudo().write({'standard_price': new_std_price})

    @api.one
    def action_done(self):
        for line in self.cost_lines:
            if self.cost_update_type == 'direct':
                line.move_id.quant_ids._price_update(line.standard_price_new)
                self._product_price_update(
                    line.move_id, line.standard_price_new)
                line.move_id.product_price_update_after_done()
        self.state = 'done'

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.one
    def action_cancel(self):
        for line in self.cost_lines:
            if self.cost_update_type == 'direct':
                if self.currency_id.compare_amounts(
                        line.move_id.quant_ids[0].cost,
                        line.standard_price_new) != 0:
                    raise exceptions.Warning(
                        _('Cost update cannot be undone because there has '
                          'been a later update. Restore correct price and try '
                          'again.'))
                line.move_id.quant_ids._price_update(line.standard_price_old)
                self._product_price_update(
                    line.move_id, line.standard_price_old)
                line.move_id.product_price_update_after_done()
        self.state = 'draft'


class PurchaseCostDistributionLine(models.Model):
    _name = "purchase.cost.distribution.line"
    _description = "Purchase cost distribution Line"

    @api.one
    @api.depends('product_price_unit', 'product_qty')
    def _compute_total_amount(self):
        self.total_amount = self.product_price_unit * self.product_qty

    @api.one
    @api.depends('product_id', 'product_qty')
    def _compute_total_weight(self):
        self.total_weight = self.product_weight * self.product_qty

    @api.one
    @api.depends('product_id', 'product_qty')
    def _compute_total_weight_net(self):
        self.total_weight_net = self.product_weight_net * self.product_qty

    @api.one
    @api.depends('product_id', 'product_qty')
    def _compute_total_volume(self):
        self.total_volume = self.product_volume * self.product_qty

    @api.one
    @api.depends('expense_lines', 'expense_lines.cost_ratio')
    def _compute_cost_ratio(self):
        self.cost_ratio = sum([x.cost_ratio for x in self.expense_lines])

    @api.one
    @api.depends('expense_lines', 'expense_lines.expense_amount')
    def _compute_expense_amount(self):
        self.expense_amount = sum([x.expense_amount for x in
                                   self.expense_lines])

    @api.one
    @api.depends('standard_price_old', 'cost_ratio')
    def _compute_standard_price_new(self):
        self.standard_price_new = self.standard_price_old + self.cost_ratio

    @api.one
    @api.depends('move_id', 'move_id.picking_id', 'move_id.product_id',
                 'move_id.product_qty')
    def _compute_display_name(self):
        self.name = '%s / %s / %s' % (
            self.move_id.picking_id.name, self.move_id.product_id.display_name,
            self.move_id.product_qty)

    @api.one
    @api.depends('move_id', 'move_id.product_id')
    def _get_product_id(self):
        # Cannot be done via related field due to strange bug in update chain
        self.product_id = self.move_id.product_id.id

    @api.one
    @api.depends('move_id', 'move_id.product_qty')
    def _get_product_qty(self):
        # Cannot be done via related field due to strange bug in update chain
        self.product_qty = self.move_id.product_qty

    @api.one
    @api.depends('move_id')
    def _get_standard_price_old(self):
        self.standard_price_old = (
            self.move_id and self.move_id.get_price_unit(self.move_id) or 0.0)

    name = fields.Char(
        string='Name', compute='_compute_display_name')
    distribution = fields.Many2one(
        comodel_name='purchase.cost.distribution', string='Cost distribution',
        ondelete='cascade')
    move_id = fields.Many2one(
        comodel_name='stock.move', string='Picking line', ondelete="restrict")
    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line', string='Purchase order line',
        related='move_id.purchase_line_id')
    purchase_id = fields.Many2one(
        comodel_name='purchase.order', string='Purchase order', readonly=True,
        related='move_id.purchase_line_id.order_id', store=True)
    partner = fields.Many2one(
        comodel_name='res.partner', string='Supplier', readonly=True,
        related='move_id.purchase_line_id.order_id.partner_id')
    picking_id = fields.Many2one(
        'stock.picking', string='Picking', related='move_id.picking_id',
        store=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', store=True,
        compute='_get_product_id')
    product_qty = fields.Float(
        string='Quantity', compute='_get_product_qty', store=True)
    product_uom = fields.Many2one(
        comodel_name='product.uom', string='Unit of measure',
        related='move_id.product_uom')
    product_uos_qty = fields.Float(
        string='Quantity (UoS)', related='move_id.product_uos_qty')
    product_uos = fields.Many2one(
        comodel_name='product.uom', string='Product UoS',
        related='move_id.product_uos')
    product_price_unit = fields.Float(
        string='Unit price', related='move_id.price_unit')
    expense_lines = fields.One2many(
        comodel_name='purchase.cost.distribution.line.expense',
        inverse_name='distribution_line', string='Expenses distribution lines',
        ondelete='cascade')
    product_volume = fields.Float(
        string='Volume', help="The volume in m3.",
        related='product_id.product_tmpl_id.volume')
    product_weight = fields.Float(
        string='Gross weight', related='product_id.product_tmpl_id.weight',
        help="The gross weight in Kg.")
    product_weight_net = fields.Float(
        string='Net weight', related='product_id.product_tmpl_id.weight_net',
        help="The net weight in Kg.")
    standard_price_old = fields.Float(
        string='Previous cost', compute="_get_standard_price_old", store=True,
        digits_compute=dp.get_precision('Product Price'))
    expense_amount = fields.Float(
        string='Cost amount', digits_compute=dp.get_precision('Account'),
        compute='_compute_expense_amount')
    cost_ratio = fields.Float(
        string='Unit cost', compute='_compute_cost_ratio')
    standard_price_new = fields.Float(
        string='New cost', digits_compute=dp.get_precision('Product Price'),
        compute='_compute_standard_price_new')
    total_amount = fields.Float(
        compute=_compute_total_amount, string='Amount line',
        digits_compute=dp.get_precision('Account'))
    total_weight = fields.Float(
        compute=_compute_total_weight, string="Line weight", store=True,
        digits_compute=dp.get_precision('Stock Weight'),
        help="The line gross weight in Kg.")
    total_weight_net = fields.Float(
        compute=_compute_total_weight_net, string='Line net weight',
        digits_compute=dp.get_precision('Stock Weight'), store=True,
        help="The line net weight in Kg.")
    total_volume = fields.Float(
        compute=_compute_total_volume, string='Line volume', store=True,
        help="The line volume in m3.")

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, "%s / %s" % (
                record.picking_id.name, record.product_id.name_get()[0][1])))
        return res


class PurchaseCostDistributionLineExpense(models.Model):
    _name = "purchase.cost.distribution.line.expense"
    _description = "Purchase cost distribution line expense"

    distribution_line = fields.Many2one(
        comodel_name='purchase.cost.distribution.line',
        string='Cost distribution line', ondelete="cascade")
    distribution_expense = fields.Many2one(
        comodel_name='purchase.cost.distribution.expense',
        string='Distribution expense', ondelete="cascade")
    type = fields.Many2one(
        'purchase.expense.type', string='Expense type',
        related='distribution_expense.type')
    expense_amount = fields.Float(
        string='Expense amount', default=0.0,
        digits_compute=dp.get_precision('Account'))
    cost_ratio = fields.Float('Unit cost', default=0.0)


class PurchaseCostDistributionExpense(models.Model):
    _name = "purchase.cost.distribution.expense"
    _description = "Purchase cost distribution expense"
    _rec_name = "type"

    @api.one
    @api.depends('distribution', 'distribution.cost_lines')
    def _get_imported_lines(self):
        self.imported_lines = self.env['purchase.cost.distribution.line']
        self.imported_lines |= self.distribution.cost_lines

    distribution = fields.Many2one(
        comodel_name='purchase.cost.distribution', string='Cost distribution',
        select=True, ondelete="cascade", required=True)
    ref = fields.Char(string="Reference")
    type = fields.Many2one(
        comodel_name='purchase.expense.type', string='Expense type',
        select=True, ondelete="restrict")
    calculation_method = fields.Selection(
        string='Calculation method', related='type.calculation_method',
        readonly=True)
    imported_lines = fields.Many2many(
        comodel_name='purchase.cost.distribution.line',
        string='Imported lines', compute='_get_imported_lines')
    affected_lines = fields.Many2many(
        comodel_name='purchase.cost.distribution.line', column1="expense_id",
        relation="distribution_expense_aff_rel", column2="line_id",
        string='Affected lines',
        help="Put here specific lines that this expense is going to be "
             "distributed across. Leave it blank to use all imported lines.",
        domain="[('id', 'in', imported_lines[0][2])]")
    expense_amount = fields.Float(
        string='Expense amount', digits_compute=dp.get_precision('Account'),
        required=True)
    invoice_line = fields.Many2one(
        comodel_name='account.invoice.line', string="Supplier invoice line",
        domain="[('invoice_id.type', '=', 'in_invoice'),"
               "('invoice_id.state', 'in', ('open', 'paid'))]")
    invoice_id = fields.Many2one(
        comodel_name='account.invoice', string="Invoice")

    @api.onchange('type')
    def onchange_type(self):
        if self.type and self.type.default_amount:
            self.expense_amount = self.type.default_amount

    @api.onchange('invoice_line')
    def onchange_invoice_line(self):
        self.invoice_id = self.invoice_line.invoice_id.id
        self.expense_amount = self.invoice_line.price_subtotal

    @api.multi
    def button_duplicate(self):
        for expense in self:
            expense.copy()
