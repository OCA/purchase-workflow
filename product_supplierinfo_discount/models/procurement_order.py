# -*- coding: utf-8 -*-
# Copyright (c) 2016 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                    Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#                    Andrius Preimantas <andrius@versada.lt>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _get_po_line_values_from_proc(
            self, procurement, partner, company, schedule_date):
        # Include discount in Purchase Order Line created from procurement
        to_ret = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        discount = self.env['purchase.order.line']._get_product_discount(
            procurement.product_id.id, to_ret['product_qty'], partner.id)
        if discount is not None:
            to_ret['discount'] = discount
        return to_ret
