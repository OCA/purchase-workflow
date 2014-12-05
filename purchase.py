# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp.osv import orm, fields


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
                                 context=None):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, context=context)
        res['prodlot_id'] = order_line.prodlot_id.id
        return res


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'prodlot_id': fields.many2one(
            'stock.production.lot',
            string='Serial Number',
            readonly=True
        )
    }


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        """ method comes from purchase/purchase.py
        """
        if procurement.product_id.track_from_sale:
            line_vals['prodlot_id'] = procurement.move_id.prodlot_id.id
        return super(ProcurementOrder, self).create_procurement_purchase_order(
            cr, uid, procurement, po_vals, line_vals, context=context)
