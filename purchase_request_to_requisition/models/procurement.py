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


class Procurement(orm.Model):
    _inherit = "procurement.order"


class procurement_order(orm.Model):
    _inherit = 'procurement.order'
    _columns = {
        'request_id': fields.many2one('purchase.request',
                                      'Latest Purchase Request')
    }

    def _get_warehouse(self, procurement, user_company):
        """
            Return the warehouse containing the procurment stock location
            (or one of it ancestors)
            If none match, returns then first warehouse of the company
        """
        company_id = (procurement.company_id or user_company).id
        domains = [
            [
                '&', ('company_id', '=', company_id),
                '|', '&', ('lot_stock_id.parent_left', '<',
                           procurement.location_id.parent_left),
                          ('lot_stock_id.parent_right', '>',
                           procurement.location_id.parent_right),
                     ('lot_stock_id', '=', procurement.location_id.id)
            ],
            [('company_id', '=', company_id)]
        ]

        cr, uid = procurement._cr, procurement._uid
        context = procurement._context
        Warehouse = self.pool['stock.warehouse']
        for domain in domains:
            ids = Warehouse.search(cr, uid, domain, context=context)
            if ids:
                return ids[0]
        return False

    def _prepare_purchase_request_line(self, cr, uid, procurement,
                                       context=None):
        return {
                'product_id': procurement.product_id.id,
                'name': procurement.product_id.name,
                'date_required': procurement.date_planned,
                'product_uom_id': procurement.product_uom.id,
                'product_qty': procurement.product_qty
        }

    def _prepare_purchase_request(self, cr, uid, procurement, context=None):
        user_company = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        request_line_data = self._prepare_purchase_request_line(
            cr, uid, procurement, context=context)
        return {
            'origin': procurement.origin,
            'company_id': procurement.company_id.id,
            'warehouse_id': self._get_warehouse(procurement, user_company),
            'line_ids': [(0, 0, request_line_data)]
        }

    def make_po(self, cr, uid, ids, context=None):
        res = {}
        request_obj = self.pool['purchase.request']
        non_request = []
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.purchase_request:
                request_data = self._prepare_purchase_request(
                    cr, uid, procurement, context=context)
                req = request_obj.create(cr, uid, request_data,
                                         context=context),
                self.message_post(cr, uid, [procurement.id],
                                  body=_("Purchase Request created"),
                                  context=context)
                procurement.write({
                    'state': 'running',
                    'request_id': req
                })
                res[procurement.id] = 0
            else:
                non_request.append(procurement.id)

        if non_request:
            res.update(super(procurement_order, self).make_po(
                cr, uid, non_request, context=context))
        return res
