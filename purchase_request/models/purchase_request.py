# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('done', 'Done')
]


class PurchaseRequest(models.Model):

    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('purchase.request')

    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or \
            self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'),
                                 ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id', '=', False)])
        return types[:1]

    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'approved', 'rejected', 'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char('Request Reference', required=True,
                       default=_get_default_name,
                       track_visibility='onchange')
    origin = fields.Char('Source Document')
    date_start = fields.Date('Creation date',
                             help="Date when the user initiated the "
                                  "request.",
                             default=fields.Date.context_today,
                             track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   copy=False,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    assigned_to = fields.Many2one(
        'res.users', 'Approver', track_visibility='onchange',
        domain=lambda self: [('groups_id', 'in', self.env.ref(
            'purchase_request.group_purchase_request_manager').id)]
    )
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True,
                                 default=_company_get,
                                 track_visibility='onchange')
    line_ids = fields.One2many('purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    product_id = fields.Many2one('product.product',
                                 related='line_ids.product_id',
                                 string='Product', readonly=True)
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
    is_editable = fields.Boolean(string="Is editable",
                                 compute="_compute_is_editable",
                                 readonly=True)
    to_approve_allowed = fields.Boolean(
        compute='_compute_to_approve_allowed')
    picking_type_id = fields.Many2one('stock.picking.type',
                                      'Picking Type', required=True,
                                      default=_default_picking_type)
    group_id = fields.Many2one('procurement.group', string="Procurement Group",
                               copy=False)
    line_count = fields.Integer(
        string='Purchase Request Line count',
        compute='_compute_line_count',
        readonly=True
    )
    move_count = fields.Integer(
        string='Stock Move count',
        compute='_compute_move_count',
        readonly=True
    )
    purchase_count = fields.Integer(
        string='Purchases count',
        compute='_compute_purchase_count',
        readonly=True
    )

    @api.depends('line_ids')
    def _compute_purchase_count(self):
        self.purchase_count = len(self.mapped(
            'line_ids.purchase_lines.order_id'))

    @api.multi
    def action_view_purchase_order(self):
        action = self.env.ref(
            'purchase.purchase_rfq').read()[0]
        lines = self.mapped('line_ids.purchase_lines.order_id')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'purchase.purchase_order_form').id, 'form')]
            action['res_id'] = lines.id
        return action

    @api.depends('line_ids')
    def _compute_move_count(self):
        self.move_count = len(self.mapped(
            'line_ids.purchase_request_allocation_ids.stock_move_id'))

    @api.multi
    def action_view_stock_move(self):
        action = self.env.ref(
            'stock.stock_move_action').read()[0]
        # remove default filters
        action['context'] = {}
        lines = self.mapped(
            'line_ids.purchase_request_allocation_ids.stock_move_id')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'stock.view_move_form').id, 'form')]
            action['res_id'] = lines.id
        return action

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped('line_ids'))

    @api.multi
    def action_view_purchase_request_line(self):
        action = self.env.ref(
            'purchase_request.purchase_request_line_form_action').read()[0]
        lines = self.mapped('line_ids')
        if len(lines) > 1:
            action['domain'] = [('id', 'in', lines.ids)]
        elif lines:
            action['views'] = [(self.env.ref(
                'purchase_request.purchase_request_line_form').id, 'form')]
            action['res_id'] = lines.ids[0]
        return action

    @api.multi
    @api.depends(
        'state',
        'line_ids.product_qty',
        'line_ids.cancelled',
    )
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = (
                rec.state == 'draft' and
                any([
                    not line.cancelled and line.product_qty
                    for line in rec.line_ids
                ])
            )

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({
            'state': 'draft',
            'name': self.env['ir.sequence'].next_by_code('purchase.request'),
        })
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to
        user_id = user_id or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        request = super(PurchaseRequest, self).create(vals)
        if vals.get('assigned_to'):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    @api.multi
    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('assigned_to'):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    @api.multi
    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == 'draft'

    @api.multi
    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(_(
                    'You cannot delete a purchase request which is not draft.'
                ))
        return super(PurchaseRequest, self).unlink()

    @api.multi
    def button_draft(self):
        self.mapped('line_ids').do_uncancel()
        return self.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        self.to_approve_allowed_check()
        return self.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        return self.write({'state': 'approved'})

    @api.multi
    def button_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    @api.multi
    def button_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({'state': 'rejected'})

    @api.multi
    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _("You can't request an approval for a purchase request "
                      "which is empty. (%s)") % rec.name)
