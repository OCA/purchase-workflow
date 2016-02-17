# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp import api, fields, models
import time
import openerp.addons.decimal_precision as dp
_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
]


class PurchaseRequest(models.Model):

    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id)

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].get('purchase.request')

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
    @api.depends('name', 'origin', 'date_start',
                 'requested_by', 'assigned_to', 'description', 'company_id',
                 'line_ids', 'picking_type_id')
    def _get_is_editable(self):
        if self.state in ('to_approve', 'approved', 'rejected'):
            self.is_editable = False
        else:
            self.is_editable = True

    _track = {
        'state': {
            'purchase_request.mt_request_to_approve':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'to_approve',
            'purchase_request.mt_request_approved':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'approved',
            'purchase_request.mt_request_rejected':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'rejected',
        },
    }

    name = fields.Char('Request Reference', size=32, required=True,
                       default=_get_default_name,
                       track_visibility='onchange')
    origin = fields.Char('Source Document', size=32)
    date_start = fields.Date('Creation date',
                             help="Date when the user initiated the "
                                  "request.",
                             default=lambda *args:
                             time.strftime('%Y-%m-%d %H:%M:%S'),
                             track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    assigned_to = fields.Many2one('res.users', 'Approver',
                                  track_visibility='onchange')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True,
                                 default=_company_get,
                                 track_visibility='onchange')
    line_ids = fields.One2many('purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               track_visibility='onchange')
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             track_visibility='onchange',
                             required=True,
                             default='draft')
    is_editable = fields.Boolean(string="Is editable",
                                 compute="_get_is_editable",
                                 readonly=True)

    picking_type_id = fields.Many2one('stock.picking.type',
                                      'Picking Type', required=True,
                                      default=_default_picking_type)

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'state': 'draft',
            'name': self.env['ir.sequence'].get('purchase.request'),
        })
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def create(self, vals):
        if vals.get('assigned_to'):
            assigned_to = self.env['res.users'].browse(vals.get(
                'assigned_to'))
            vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        return super(PurchaseRequest, self).create(vals)

    @api.one
    def write(self, vals):
        if vals.get('assigned_to'):
            assigned_to = self.env['res.users'].browse(
                vals.get('assigned_to'))
            vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        res = super(PurchaseRequest, self).write(vals)
        return res

    @api.multi
    def button_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def button_to_approve(self):
        self.state = 'to_approve'
        return True

    @api.multi
    def button_approved(self):
        self.state = 'approved'
        return True

    @api.multi
    def button_rejected(self):
        self.state = 'rejected'
        return True


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.multi
    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
                 'analytic_account_id', 'date_required', 'specifications')
    def _get_is_editable(self):
        if self.request_id.state in ('to_approve', 'approved', 'rejected'):
            self.is_editable = False
        else:
            self.is_editable = True

    @api.one
    def _get_supplier(self):
        if self.product_id:
            for product_supplier in self.product_id.seller_ids:
                self.supplier_id = product_supplier.name

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', True)],
        track_visibility='onchange')
    name = fields.Char('Description', size=256,
                       track_visibility='onchange')
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',
                                     track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'))
    request_id = fields.Many2one('purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',
                                 related='request_id.company_id',
                                 string='Company',
                                 store=True, readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account',
                                          track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Requested by',
                                   store=True, readonly=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True, readonly=True)
    date_start = fields.Date(related='request_id.date_start',
                             string='Request Date', readonly=True,
                             store=True)
    description = fields.Text(related='request_id.description',
                              string='Description', readonly=True,
                              store=True)
    origin = fields.Char(related='request_id.origin',
                         size=32, string='Source Document', readonly=True,
                         store=True)
    date_required = fields.Date(string='Request Date', required=True,
                                track_visibility='onchange',
                                default=lambda *args: time.strftime(
                                    '%Y-%m-%d %H:%M:%S'))
    is_editable = fields.Boolean(string='Is editable',
                                 compute="_get_is_editable",
                                 readonly=True)
    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state',
                                     readonly=True,
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier',
                                  compute="_get_supplier")

    procurement_id = fields.Many2one('procurement.order',
                                     'Procurement Order',
                                     readonly=True)

    @api.onchange('product_id', 'product_uom_id')
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
