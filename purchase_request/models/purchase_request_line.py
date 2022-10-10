# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare


_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('done', 'Done')
]


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Description', track_visibility='onchange')
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure',
                                     track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'))
    request_id = fields.Many2one('purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',
                                 related='request_id.company_id',
                                 string='Company',
                                 store=True)
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account',
                                          track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Requested by',
                                   store=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True)
    date_start = fields.Date(related='request_id.date_start',
                             store=True)
    description = fields.Text(related='request_id.description',
                              string='PR Description',
                              store=True, readonly=False)
    origin = fields.Char(related='request_id.origin',
                         string='Source Document', store=True)
    date_required = fields.Date(string='Request Date', required=True,
                                track_visibility='onchange',
                                default=fields.Date.context_today)
    is_editable = fields.Boolean(string='Is editable',
                                 compute="_compute_is_editable",
                                 readonly=True)
    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state',
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier',
                                  compute="_compute_supplier_id")
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False)

    purchased_qty = fields.Float(
        string='Quantity in RFQ or PO',
        digits=dp.get_precision('Product Unit of Measure'),
        compute="_compute_purchased_qty")
    purchase_lines = fields.Many2many(
        'purchase.order.line', 'purchase_request_purchase_order_line_rel',
        'purchase_request_line_id',
        'purchase_order_line_id', 'Purchase Order Lines',
        readonly=True, copy=False)
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self:
        self.env['purchase.order']._fields['state'].selection,
        store=True,
    )
    move_dest_ids = fields.One2many('stock.move',
                                    'created_purchase_request_line_id',
                                    'Downstream Moves')

    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'Orderpoint')
    purchase_request_allocation_ids = fields.One2many(
        comodel_name='purchase.request.allocation',
        inverse_name='purchase_request_line_id',
        string='Purchase Request Allocation')

    qty_in_progress = fields.Float(
        'Qty In Progress', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute='_compute_qty', store=True,
        help="Quantity in progress.",
    )
    qty_done = fields.Float(
        'Qty Done', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute='_compute_qty', store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        'Qty Cancelled', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, compute='_compute_qty_cancelled', store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute='_compute_qty_to_buy',
        string="There is some pending qty to buy",
        store=True
    )
    pending_qty_to_receive = fields.Float(
        compute='_compute_qty_to_buy',
        digits=dp.get_precision('Product Unit of Measure'),
        copy=False,
        string="Pending Qty to Receive", store=True)

    @api.depends('purchase_request_allocation_ids',
                 'purchase_request_allocation_ids.stock_move_id.state',
                 'purchase_request_allocation_ids.stock_move_id',
                 'purchase_request_allocation_ids.purchase_line_id.state',
                 'purchase_request_allocation_ids.purchase_line_id')
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped('product_qty')) - \
                sum(pr.mapped('qty_done'))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends('purchase_request_allocation_ids',
                 'purchase_request_allocation_ids.stock_move_id.state',
                 'purchase_request_allocation_ids.stock_move_id',
                 'purchase_request_allocation_ids.purchase_line_id.state',
                 'purchase_request_allocation_ids.purchase_line_id')
    def _compute_qty(self):
        for request in self:
            done_qty = sum(request.purchase_request_allocation_ids.mapped(
                'allocated_product_qty'))
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped(
                    'open_product_qty'))
            if request.product_uom_id:
                request.qty_done = request.product_id.uom_id._compute_quantity(
                    done_qty, request.product_uom_id)
                request.qty_in_progress = \
                    request.product_id.uom_id._compute_quantity(
                        open_qty, request.product_uom_id)
            else:
                request.qty_done = done_qty
                request.qty_in_progress = open_qty

    @api.depends('purchase_request_allocation_ids',
                 'purchase_request_allocation_ids.stock_move_id.state',
                 'purchase_request_allocation_ids.stock_move_id',
                 'purchase_request_allocation_ids.purchase_line_id.order_id.'
                 'state',
                 'purchase_request_allocation_ids.purchase_line_id')
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != 'service':
                qty_cancelled = sum(request.mapped(
                    'purchase_request_allocation_ids.stock_move_id').filtered(
                    lambda sm: sm.state == 'cancel').mapped('product_qty'))
            else:
                qty_cancelled = sum(request.mapped(
                    'purchase_request_allocation_ids.purchase_line_id'
                ).filtered(
                    lambda sm: sm.state == 'cancel').mapped('product_qty'))
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = max(
                    0, request.product_id.uom_id._compute_quantity(
                        qty_cancelled, request.product_uom_id
                    )) if request.purchase_request_allocation_ids else 0
            else:
                request.qty_cancelled = qty_cancelled

    def check_done(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for request in self:
            allocated_qty = sum(
                request.purchase_request_allocation_ids.mapped(
                    'allocated_product_qty'))
            if request.product_uom_id:
                qty_done = request.product_id.uom_id._compute_quantity(
                    allocated_qty, request.product_uom_id)
            else:
                qty_done = allocated_qty
            if float_compare(qty_done, request.product_qty,
                             precision_digits=precision) >= 0:
                request.set_done()
        return True

    estimated_cost = fields.Monetary(
        string='Estimated Cost', currency_field='currency_id', default=0.0,
        help='Estimated cost of Purchase Request Line, not propagated to PO.')
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )

    @api.multi
    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
                 'analytic_account_id', 'date_required', 'specifications',
                 'purchase_lines')
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to_approve', 'approved', 'rejected',
                                        'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    @api.multi
    def _compute_supplier_id(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.seller_ids:
                    rec.supplier_id = rec.product_id.seller_ids[0].name

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', True)],
        track_visibility='onchange')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name

    @api.multi
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({'cancelled': True})

    @api.multi
    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({'cancelled': False})

    @api.multi
    def write(self, vals):
        res = super(PurchaseRequestLine, self).write(vals)
        if vals.get('cancelled'):
            requests = self.mapped('request_id')
            requests.check_auto_reject()
        return res

    @api.multi
    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(
                    lambda x: x.state != 'cancel'):
                if rec.product_uom_id and\
                        line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id)
                else:
                    rec.purchased_qty += line.product_qty

    @api.multi
    @api.depends('purchase_lines.state', 'purchase_lines.order_id.state')
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any([po_line.state == 'done' for po_line in
                        rec.purchase_lines]):
                    temp_purchase_state = 'done'
                elif all([po_line.state == 'cancel' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'cancel'
                elif any([po_line.state == 'purchase' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'purchase'
                elif any([po_line.state == 'to approve' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'to approve'
                elif any([po_line.state == 'sent' for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'sent'
                elif all([po_line.state in ('draft', 'cancel') for po_line in
                          rec.purchase_lines]):
                    temp_purchase_state = 'draft'
            rec.purchase_state = temp_purchase_state

    @api.model
    def _planned_date(self, request_line, delay=0.0):
        company = request_line.company_id
        date_planned = datetime.strptime(
            request_line.date_required, '%Y-%m-%d') - \
            relativedelta(days=company.po_lead)
        if delay:
            date_planned -= relativedelta(days=delay)
        return date_planned and date_planned.strftime('%Y-%m-%d') \
            or False

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids \
                .filtered(lambda r: r.name == partner_id) \
                .sorted(key=lambda r: r.min_qty)
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None,
                      new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        uom = request_line.product_uom_id
        qty = uom._compute_quantity(request_line.product_qty, purchase_uom)
        # Make sure we use the minimum quantity of the partner corresponding
        # to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id)

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        for rl in po_line.purchase_request_lines:
            rl_qty += rl.product_uom_id._compute_quantity(
                rl.product_qty, purchase_uom)
        qty = max(rl_qty, supplierinfo_min_qty)
        return qty

    @api.multi
    def unlink(self):
        if self.mapped('purchase_lines'):
            raise UserError(
                _('You cannot delete a record that refers to purchase '
                  'lines!'))
        return super(PurchaseRequestLine, self).unlink()
