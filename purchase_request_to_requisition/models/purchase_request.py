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
from openerp.tools.translate import _

_PURCHASE_REQUISITION_STATE = [
    ('none', 'No Bid'),
    ('draft', 'New'),
    ('in_progress', 'Sent to Suppliers'),
    ('cancel', 'Cancelled'),
    ('done', 'Purchase Done'),
]


class PurchaseRequestLine(orm.Model):

    _inherit = "purchase.request.line"

    def _get_is_editable(self, cr, uid, ids, names, arg, context=None):
        res = super(PurchaseRequestLine, self)._get_is_editable(
            cr, uid, ids, names, arg, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            if line.requisition_lines:
                res[line.id] = False
        return res

    def _requisition_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for request_line in self.browse(cursor, user, ids, context=context):
            requisition_qty = 0.0
            for requisition_line in request_line.requisition_lines:
                if requisition_line.requisition_id.state != 'cancel':
                    requisition_qty += requisition_line.product_qty
            res[request_line.id] = requisition_qty
        return res

    def _get_requisition_state(self, cr, uid, ids, names, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 'none'
            if any([pr_line.requisition_id.state == 'done' for
                    pr_line in
                    line.requisition_lines]):
                res[line.id] = 'done'
            elif all([pr_line.requisition_id.state == 'cancel'
                      for pr_line in line.requisition_lines]):
                res[line.id] = 'cancel'
            elif any([pr_line.requisition_id.state == 'in_progress'
                      for pr_line in line.requisition_lines]):
                res[line.id] = 'in_progress'
            elif all([pr_line.requisition_id.state in ('draft', 'cancel')
                      for pr_line in line.requisition_lines]):
                res[line.id] = 'draft'
        return res

    def _get_request_lines_from_pr(self, cr, uid, ids, context=None):
        request_line_ids = []
        for requisition in self.pool['purchase.requisition'].browse(
                cr, uid, ids, context=context):
            for line in requisition.line_ids:
                for request_line in line.purchase_request_lines:
                    request_line_ids.append(request_line.id)
        return list(set(request_line_ids))

    def _get_request_lines_from_prl(self, cr, uid, ids, context=None):
        request_line_ids = []
        for rl in self.pool['purchase.requisition.line'].browse(
                cr, uid, ids, context=context):
            for request_line in rl.purchase_request_lines:
                request_line_ids.append(request_line.id)
        return list(set(request_line_ids))

    _columns = {
        'requisition_lines': fields.many2many(
            'purchase.requisition.line',
            'purchase_request_purchase_requisition_line_rel',
            'purchase_request_line_id',
            'purchase_requisition_line_id',
            'Purchase Requisition Lines', readonly=True),
        'requisition_qty': fields.function(_requisition_qty,
                                           string='Quantity in a Bid',
                                           type='float'),
        'requisition_state': fields.function(
            _get_requisition_state, string="Bid Status",
            type="selection",
            selection=_PURCHASE_REQUISITION_STATE,
            store={'purchase.requisition': (
                _get_request_lines_from_pr,
                ['state', 'line_ids'], 10),
                'purchase.requisition.line': (
                _get_request_lines_from_prl, ['purchase_request_lines'],
                10)},),
        'is_editable': fields.function(_get_is_editable,
                                       string="Is editable",
                                       type="boolean")
    }

    _defaults = {
        'requisition_state': 'none',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'requisition_lines': [],
        })
        return super(PurchaseRequestLine, self).copy(
            cr, uid, id, default, context)

    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.requisition_lines:
                raise orm.except_orm(
                    _('Error!'),
                    _('You cannot delete a record that refers to purchase '
                      'requisition lines!'))
        return super(PurchaseRequestLine, self).unlink(cr, uid, ids,
                                                       context=context)
