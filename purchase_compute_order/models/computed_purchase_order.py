##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from math import ceil
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class ComputedPurchaseOrder(models.Model):
    _description = 'Computed Purchase Order'
    _name = 'computed.purchase.order'
    _order = 'id desc'

    # Constant Values
    _DEFAULT_NAME = _('New')

    _STATE = [
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ]

    _TARGET_TYPE = [
        ('product_price_inv_eq', '€'),
        ('time', 'days'),
        ('weight', 'kg'),
    ]

    _VALID_PSI = [
        ('first', 'Consider only the first supplier on the product'),
        ('all', 'Consider all the suppliers registered on the product'),
    ]

    # Columns section
    name = fields.Char(
        'Computed Purchase Order Reference', size=64, required=True,
        readonly=True, default=_DEFAULT_NAME,
        help="""Unique number of the automated purchase order, computed"""
        """ automatically when the computed purchase order is created.""")
    company_id = fields.Many2one(
        'res.company', 'Company', readonly=True, required=True,
        help="""When you will validate this item, this will create a"""
        """ purchase order for this company.""",
        default=lambda self: self.env.user.company_id,)
    active = fields.Boolean(
        default=True,
        help="""By unchecking the active field, you may hide this item"""
        """ without deleting it.""")
    state = fields.Selection(_STATE, required=True, default='draft')
    incoming_date = fields.Date(
        'Wished Incoming Date',
        help="Wished date for products delivery.")
    partner_id = fields.Many2one(
        'res.partner', 'Supplier', required=True,
        domain=[('supplier', '=', True)],
        help="Supplier of the purchase order.")
    line_ids = fields.One2many(
        comodel_name='computed.purchase.order.line',
        inverse_name='computed_purchase_order_id',
        string='Order Lines', help="Products to order.")
    # this is to be able to display the line_ids on 2 tabs of the view
    stock_line_ids = fields.One2many(
        compute='_compute_stock_line_ids',
        comodel_name='computed.purchase.order.line',
        inverse_name='computed_purchase_order_id',
        help="Products to order.")
    compute_pending_quantity = fields.Boolean(
        'Pending quantity taken in account', default=True)
    purchase_order_id = fields.Many2one(
        'purchase.order', 'Purchase Order', readonly=True)
    purchase_target = fields.Integer(default=0)
    target_type = fields.Selection(
        _TARGET_TYPE, required=True,
        default='product_price_inv_eq',
        help="""This defines the amount of products you want to"""
        """ purchase. \n"""
        """The system will compute a purchase order based on the stock"""
        """ you have and the average consumption of each product."""
        """ * Target type '€': computed purchase order will cost at"""
        """ least the amount specified\n"""
        """ * Target type 'days': computed purchase order will last"""
        """ at least the number of days specified (according to current"""
        """ average consumption)\n"""
        """ * Target type 'kg': computed purchase order will weight at"""
        """ least the weight specified""")
    line_order_field = fields.Selection(
        [
            ('product_code', 'Supplier Product Code'),
            ('product_name', 'Supplier Product Name'),
            ('product_sequence', 'Product Sequence'),
        ],
        string='Lines Order',
        help='The field used to sort the CPO lines',
        default='product_code',
        required=True,
    )
    line_order = fields.Selection(
        [
            ('asc', 'Ascending'),
            ('desc', 'Descending'),
        ],
        string='Lines Order Direction',
        default='asc',
        required=True,
    )
    valid_psi = fields.Selection(
        _VALID_PSI, 'Supplier choice', required=True,
        default='first',
        help="""Method of selection of suppliers""")
    computed_amount = fields.Float(
        compute='_compute_computed_amount_duration',
        digits=dp.get_precision('Product Price'),
        string='Amount of the computed order')
    package_qty_count = fields.Float(
        string='Total Quantity of Packages',
        help='Total count of packages by the current vendor',
        compute='_compute_package_quantity_count',
        readonly='True',
    )
    computed_duration = fields.Integer(
        compute='_compute_computed_amount_duration',
        string='Minimum duration after order')
    products_updated = fields.Boolean(
        compute='_compute_products_updated',
        string='Indicate if there were any products updated in the list')
    lines_with_qty_count = fields.Integer(
        'Total Ordered Lines',
        compute='_compute_lines_with_qty',
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        # we don't need to recompute the whole CPO after changing a line
        if field_name == "line_ids":
            return {}
        return super().onchange(
            values, field_name, field_onchange,
        )

    # Fields Function section
    @api.onchange('line_ids')
    @api.multi
    def _compute_stock_line_ids(self):
        for spo in self:
            spo.stock_line_ids = spo.line_ids

    @api.multi
    def _compute_computed_amount_duration(self):
        for cpo in self:
            min_duration = 999
            amount = 0
            for line in cpo.line_ids:
                if line.average_consumption != 0:
                    duration = (line.computed_qty + line.purchase_qty)\
                        / line.average_consumption
                    min_duration = min(duration, min_duration)
                amount += line.subtotal
            cpo.computed_amount = amount
            cpo.computed_duration = min_duration

    @api.multi
    def _compute_products_updated(self):
        for cpo in self:
            updated = False
            for line in cpo.line_ids:
                if line.state == 'updated':
                    updated = True
                    break
            cpo.products_updated = updated

    @api.depends('line_ids.purchase_qty')
    def _compute_lines_with_qty(self):
        for cpo in self:
            cpo.lines_with_qty_count = len(cpo.line_ids.filtered(
                lambda line: line.purchase_qty > 0))

    # View Section
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        # TODO: create a wizard to validate the change
        self.purchase_target = 0
        self.target_type = 'product_price_inv_eq'
        if self.partner_id:
            self.purchase_target = self.partner_id.purchase_target
            self.target_type = self.partner_id.target_type
            self.line_order_field = self.partner_id.cpo_line_order_field
            self.line_order = self.partner_id.cpo_line_order
        self.line_ids = [(2, x.id, False) for x in self.line_ids]

    # Overload Section
    @api.model
    def create(self, vals):
        if vals.get('name', self._DEFAULT_NAME) == self._DEFAULT_NAME:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'computed.purchase.order') or '/'
        order = super(ComputedPurchaseOrder, self).create(vals)
        return order

    @api.multi
    def write(self, vals):
        cpo_id = super(ComputedPurchaseOrder, self).write(vals)
        if self.update_sorting(vals):
            self.sort_lines()
        return cpo_id

    @api.multi
    def sort_lines(self):
        for rec in self:
            # sort based on field
            lines = rec.line_ids.sorted(
                key=lambda l: getattr(l, rec.line_order_field) or '',
                reverse=(rec.line_order == 'desc'))
            # store new sequence
            for i, line in enumerate(lines):
                line.sequence = i

    @api.model
    def update_sorting(self, vals):
        try:
            line_ids = vals.get('line_ids', False)
            if not line_ids:
                return False
            # this context check will allow you to change the field list
            # without overriding the whole function
            need_sorting_fields = self.env.context.get(
                'need_sorting_fields', False)
            if not need_sorting_fields:
                need_sorting_fields = [
                    'average_consumption',
                    'computed_qty',
                    'stock_duration',
                    'manual_input_output_qty',
                    'product_id',
                ]
            for value in line_ids:
                if len(value) > 2 and value[2] and isinstance(
                        value[2], dict) and (set(
                        need_sorting_fields) & set(value[2].keys())):
                    return True
            return False
        except Exception:
            return False

    # Private Section
    @api.multi
    def _sort_lines(self):
        cpol_obj = self.env['computed.purchase.order.line']
        for cpo in self:
            lines = cpol_obj.browse([x.id for x in cpo.line_ids]).read(
                ['stock_duration', 'average_consumption'])
            lines = sorted(
                lines, key=lambda line: line['average_consumption'],
                reverse=True)
            lines = sorted(lines, key=lambda line: line['stock_duration'])

            id_index_list = {}
            for i in lines:
                id_index_list[i['id']] = lines.index(i)
            for line_id in list(id_index_list.keys()):
                cpol_obj.browse(line_id).write(
                    {'sequence': id_index_list[line_id]})

    @api.model
    def _make_po_lines(self):
        all_lines = []
        for line in self.line_ids:
            if line.purchase_qty != 0:
                line_values = {
                    'name': "%s%s" % (
                        line.product_code_inv and
                            '[' + line.product_code_inv + '] ' or '',
                        line.product_name_inv or
                            line.product_id.name),
                    'product_qty': line.purchase_qty,
                    'package_qty': line.package_qty,
                    'product_qty_package': (
                        line.purchase_qty / line.package_qty),
                    'price_policy': line.price_policy,
                    'date_planned': (
                        self.incoming_date or fields.Date.context_today(self)),
                    'product_uom': line.product_id.uom_po_id.id,
                    'product_id': line.product_id.id,
                    'price_unit': line.product_price_inv,
                    'discount': line.discount_inv,
                    'taxes_id': [(
                        6, 0,
                        [x.id for x in line.product_id.supplier_taxes_id])],
                }
                all_lines.append((0, 0, line_values),)
        return all_lines

    def parse_qty(self, cpo_line, days):
        if cpo_line.average_consumption:
            quantity = max(
                days * cpo_line.average_consumption *
                cpo_line.uom_po_id.factor / cpo_line.uom_id.factor -
                cpo_line.computed_qty, 0)
            if cpo_line.package_qty \
                    and quantity % cpo_line.package_qty:
                quantity = ceil(quantity / cpo_line.package_qty) *\
                    cpo_line.package_qty
        elif cpo_line.computed_qty == 0:
            quantity = cpo_line.package_qty or 0
        else:
            quantity = 0
        return quantity, cpo_line.product_price, cpo_line.psi_id, cpo_line.package_qty

    @api.multi
    def _compute_purchase_quantities_days(self):
        for cpo in self:
            days = cpo.purchase_target
            for line in cpo.line_ids:
                line = line.with_context(update_price=True)
                quantity, product_price, psi, package_qty = self.parse_qty(line, days)
                line.psi_id = psi
                line.purchase_qty = quantity
                line.purchase_qty_package = quantity / package_qty
                line.package_qty = package_qty
                line.product_price = product_price

    @api.multi
    @api.depends('line_ids.purchase_qty_package')
    def _compute_package_quantity_count(self):
        for rec in self:
            rec.package_qty_count = sum(rec.mapped(
                'line_ids.purchase_qty_package'))

    def _update_field_list_dict_price(self, field_list_dict, line, line_qty_tmp):
        product_price_inv_eq = 0
        quantity, product_price, psi, package_qty = line_qty_tmp
        if line.price_policy == 'package':
            purchase_qty_package = quantity / package_qty
            if purchase_qty_package:
                product_price_inv_eq = product_price /\
                    purchase_qty_package
        else:
            product_price_inv_eq = product_price
        field_list_dict[line.id] = product_price_inv_eq

    @api.multi
    def _compute_purchase_quantities_other(self, field):
        for cpo in self:
            cpol_obj = self.env['computed.purchase.order.line']
            if not cpo.line_ids:
                return False
            target = cpo.purchase_target
            ok = False
            days = -1
            field_list = cpol_obj.browse(
                [x.id for x in cpo.line_ids]).read([field])
            field_list_dict = {}
            for i in field_list:
                field_list_dict[i['id']] = i[field]

            last_total_qty = 0
            same_qty = 0
            while not ok:
                days += 1
                qty_tmp = {}
                qty_tmp_tocheck = {}
                total_qty = 0
                for line in cpo.line_ids:
                    qty_tmp[line.id] = self.parse_qty(line, days)
                    qty_tmp_tocheck[line.id] = qty_tmp[line.id][0]
                    total_qty += qty_tmp[line.id][0]
                    if field == 'product_price_inv_eq':
                        self._update_field_list_dict_price(
                            field_list_dict, line, qty_tmp[line.id])
                if last_total_qty and last_total_qty == total_qty:
                    # This break condition helps to avoid looping
                    same_qty += 1
                    if same_qty > 100:
                        break
                else:
                    same_qty = 0
                ok = cpo._check_purchase_qty(target, field_list_dict, qty_tmp_tocheck)
                last_total_qty = total_qty

            for line in cpo.line_ids:
                quantity, product_price, psi, package_qty = qty_tmp[line.id]
                line.psi_id = psi
                line.purchase_qty = quantity
                line.purchase_qty_package = quantity / package_qty
                line.package_qty = package_qty
                line.product_price = product_price

    @api.model
    def _check_purchase_qty(self, target=0, field_list=None, qty_tmp=None):
        if not target or field_list is None or qty_tmp is None:
            return True
        total = 0
        for key in list(field_list.keys()):
            total += field_list[key] * qty_tmp[key]
        if total <= 0 and qty_tmp[key] > 0:
            # in case product's weight is 0
            return True
        return total >= target

    @api.multi
    def get_psi_domain(self):
        self.ensure_one()
        args = [('name', '=', self.partner_id.id)]
        return args

    def parse_cpol_vals(self, psi, product):
        res = {
            'product_id': product.id,
            'state': 'up_to_date',
            'product_code': psi.product_code,
            'product_name': psi.product_name,
            'product_price': psi.base_price,
            'price_policy': psi.price_policy,
            'package_qty': psi.package_qty or psi.min_qty,
            'displayed_average_consumption': \
                product.displayed_average_consumption,
            'consumption_range': product.display_range,
            'uom_po_id': psi.product_uom.id,
            'psi_id': psi.id,
        }
        return res

    # Action section
    @api.multi
    def compute_active_product_stock(self):
        psi_obj = self.env['product.supplierinfo']
        for cpo in self:
            cpol_list = []
            # TMP delete all rows,
            # TODO : depends on further request to avoid user data to be lost
            cpo.line_ids.unlink()

            # Get product_product and compute stock
            for psi in psi_obj.search(cpo.get_psi_domain()):
                for pp in psi.product_tmpl_id.filtered(
                        lambda pt: pt.purchase_ok).product_variant_ids:
                    valid_psi = pp._valid_psi(cpo.valid_psi)
                    if valid_psi and psi in valid_psi[0]:
                        cpol_list.append((0, 0,
                            self.parse_cpol_vals(psi, pp)
                        ))
            # update line_ids
            self.line_ids = cpol_list

    @api.multi
    def compute_purchase_quantities(self):
        for cpo in self:
            if any([line.average_consumption for line in cpo.line_ids]):
                if cpo.target_type == 'time':
                    return cpo._compute_purchase_quantities_days()
                else:
                    return cpo._compute_purchase_quantities_other(
                        field=cpo.target_type)

    @api.multi
    def make_order(self):
        for cpo in self:
            po_lines = cpo._make_po_lines()
            if not po_lines:
                raise ValidationError(
                    _('All purchase quantities are set to 0!'))

            po_obj = self.env['purchase.order']
            po_values = {
                'origin': cpo.name,
                'partner_id': cpo.partner_id.id,
                'order_line': po_lines,
                'date_planned': (
                    cpo.incoming_date or fields.Date.context_today(self)),
            }
            po_id = po_obj.create(po_values)
            cpo.state = 'done'
            cpo.purchase_order_id = po_id

            mod_obj = self.env['ir.model.data']
            res = mod_obj.get_object_reference(
                'purchase', 'purchase_order_form')
            res_id = res and res[1] or False
            return {
                'name': _('Purchase Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(res_id, 'form')],
                'view_id': [res_id],
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': po_id.id or False,
            }

    @api.multi
    def action_view_order_lines(self):
        self.ensure_one()
        action = self.env.ref(
            'purchase_compute_order.action_computed_purchase_order_tree')
        action = action.read()[0]
        action['domain'] = [('computed_purchase_order_id', '=', self.id)]
        action['context'] = {'search_default_ordered_products': 1}
        return action
