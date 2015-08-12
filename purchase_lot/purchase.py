# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id,
                                 group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        for move in res:
            move['restrict_lot_id'] = order_line.lot_id.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_id = fields.Many2one(
            'stock.production.lot',
            string='Serial Number',
            readonly=True
        )


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _get_po_line_values_from_proc(self, procurement, partner, company,
                                      schedule_date):
        res = super(ProcurementOrder,self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        if procurement.product_id.auto_generate_prodlot:
            res['lot_id'] = procurement.lot_id.id
        return res

    @api.model
    def _get_available_draft_po_line_domain(self, po_id, line_vals):
        res = super(ProcurementOrder, self)._get_available_draft_po_line_domain(
            po_id, line_vals)
        res.append(('lot_id', '=', line_vals.get('lot_id')))
        return res
