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
from openerp.osv import fields, orm
import time
import openerp.addons.decimal_precision as dp
_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
]


class PurchaseRequest(orm.Model):

    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'purchase_request.mt_request_to_approve':
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] == 'to_approve',
            'purchase_request.mt_request_approved':
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] == 'approved',
            'purchase_request.mt_request_rejected':
                lambda self, cr, uid, obj,
                ctx=None: obj['state'] == 'rejected',
        },
    }

    def _get_is_editable(self, cr, uid, ids, names, arg, context=None):
        res = dict.fromkeys(ids, True)
        for line in self.browse(cr, uid, ids, context=context):
            if line.state in ('to_approve', 'approved', 'rejected'):
                res[line.id] = False
        return res

    _columns = {
        'name': fields.char('Request Reference', size=32, required=True),
        'origin': fields.char('Source Document', size=32),
        'created_on': fields.date('Created on',
                                  help="Date that the request was created."),
        'date_start': fields.date('Creation date',
                                  help="Date when the user initiated the "
                                       "request."),
        'requested_by': fields.many2one('res.users',
                                        'Requested by',
                                        required=True,
                                        track_visibility='onchange'),
        'assigned_to': fields.many2one('res.users', 'Assigned to',
                                       track_visibility='onchange'),
        'description': fields.text('Description'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'line_ids': fields.one2many('purchase.request.line', 'request_id',
                                    'Products to Purchase',
                                    readonly=False),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse',
                                        track_visibility='onchange'),
        'is_editable': fields.function(_get_is_editable,
                                       string="Is editable",
                                       type="boolean"),
        'state': fields.selection(_STATES, 'State', required=True,
                                  track_visibility='onchange'),
    }

    def _get_default_warehouse(self, cr, uid, context=None):
        warehouse_obj = self.pool['stock.warehouse']
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid).company_id.id
        warehouse_ids = warehouse_obj.search(
            cr, uid, [('company_id', '=', company_id)], context=context)
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    _defaults = {
        'date_start': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'company_id':
            lambda self, cr, uid, c:
            self.pool.get('res.company')._company_default_get(
                cr, uid, 'purchase.request', context=c),
        'requested_by':
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).id,
        'name':
            lambda obj, cr, uid, context:
            obj.pool.get('ir.sequence').get(
                cr, uid, 'purchase.request'),
        'state': 'draft',
        'is_editable': True,
        'warehouse_id': _get_default_warehouse,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid,
                                                     'purchase.request'),
            'state': 'draft',
        })
        return super(PurchaseRequest, self).copy(
            cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('assigned_to', False):
            assigned_to = self.pool.get('res.users').browse(
                cr, uid, vals.get('assigned_to'), context=context)
            if assigned_to.partner_id:
                vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        return super(PurchaseRequest, self).create(cr, uid, vals,
                                                   context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('assigned_to', False):
            assigned_to = self.pool.get('res.users').browse(
                cr, uid, vals.get('assigned_to'), context=context)
            if assigned_to.partner_id:
                vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        res = super(PurchaseRequest, self).write(cr, uid, ids, vals,
                                                 context=context)
        return res

    def button_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def button_to_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'to_approve'},
                          context=context)

    def button_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approved'},
                          context=context)

    def button_rejected(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'rejected'},
                          context=context)


class PurchaseRequestLine(orm.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'product_id'

    def _get_is_editable(self, cr, uid, ids, names, arg, context=None):
        res = dict.fromkeys(ids, True)
        for line in self.browse(cr, uid, ids, context=context):
            if line.request_id.state in ('to_approve', 'approved', 'rejected'):
                res[line.id] = False
        return res

    def _get_supplier(self, cr, uid, ids, names, arg, context=None):
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            if line.product_id:
                for product_supplier in line.product_id.seller_ids:
                    res[line.id] = product_supplier.name.id
                    break
        return res

    def _get_lines_from_request(self, cr, uid, ids, context=None):
        lines = []
        for request in self.pool['purchase.request'].browse(
                cr, uid, ids, context=context):
            for line in request.line_ids:
                lines.append(line.id)
        return list(set(lines))

    _columns = {
        'product_id': fields.many2one(
            'product.product', 'Product',
            domain=[('purchase_ok', '=', True)]),
        'name': fields.char('Description', size=256, required=True,
                            track_visibility='onchange'),
        'product_uom_id': fields.many2one(
            'product.uom', 'Product Unit of Measure',
            track_visibility='onchange'),
        'product_qty': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            track_visibility='onchange'),
        'request_id': fields.many2one('purchase.request',
                                      'Purchase Request',
                                      ondelete='cascade', readonly=True),
        'company_id': fields.related('request_id', 'company_id',
                                     type='many2one',
                                     relation='res.company',
                                     string='Company',
                                     readonly=True,
                                     store={'purchase.request': (
                                       _get_lines_from_request,
                                       None, 20)}),
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Analytic Account',
            track_visibility='onchange'),
        'requested_by': fields.related('request_id', 'requested_by',
                                       string='Requested by',
                                       readonly=True,
                                       type="many2one",
                                       relation="res.users",
                                       store={'purchase.request': (
                                           _get_lines_from_request,
                                           None, 20)}),
        'assigned_to': fields.related('request_id', 'assigned_to',
                                      string='Assigned to',
                                      readonly=True,
                                      type="many2one",
                                      relation="res.users",
                                      store={'purchase.request': (
                                           _get_lines_from_request,
                                           None, 20)}),
        'date_start': fields.related('request_id', 'date_start',
                                     string='Request Date', readonly=True,
                                     type="date",
                                     store={'purchase.request': (
                                           _get_lines_from_request,
                                           None, 20)}),
        'description': fields.related('request_id', 'description',
                                      string='Description',
                                      type='text',
                                      readonly=True),
        'origin': fields.related('request_id', 'origin',
                                 string='Source Document', readonly=True,
                                 type="char", size=32,
                                 store={'purchase.request': (
                                     _get_lines_from_request,
                                     None, 20)}),
        'warehouse_id': fields.related('request_id', 'warehouse_id',
                                       string='Warehouse',
                                       readonly=True,
                                       type="many2one",
                                       relation="stock.warehouse",
                                       store={'purchase.request': (
                                           _get_lines_from_request,
                                           None, 20)}),
        'date_required': fields.date('Required date',
                                     help="Date that the products are "
                                          "required to be received or "
                                          "services rendered.",
                                     required=True,
                                     track_visibility='onchange'),
        'is_editable': fields.function(_get_is_editable,
                                       string="Is editable",
                                       type="boolean"),
        'specifications': fields.text('Specifications'),
        'request_state': fields.related('request_id', 'state',
                                        string="Request state",
                                        readonly=True,
                                        type="selection",
                                        selection=_STATES,
                                        store={'purchase.request': (
                                           _get_lines_from_request,
                                           None, 20)}),
        'supplier_id': fields.function(_get_supplier,
                                       string="Preferred supplier",
                                       type="many2one",
                                       relation="res.partner",
                                       readonly=True),
    }
    _defaults = {
        'date_required': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': '',
        'is_editable': True,
    }

    def onchange_product_id(self, cr, uid, ids, product_id,
                            product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            product_obj = self.pool['product.product']
            prod = product_obj.browse(
                cr, uid, product_id, context=context)
            product_name = product_obj.name_get(cr, uid, product_id,
                                                context=context)
            dummy, name = product_name and product_name[0] or (False,
                                                               False)
            if prod.description_purchase:
                name += '\n' + prod.description_purchase

            value = {'product_uom_id': prod.uom_id.id,
                     'product_qty': 1.0,
                     'name': name}
        return {'value': value}
