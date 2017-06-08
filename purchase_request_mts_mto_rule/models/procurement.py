# -*- coding: utf-8 -*-
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_purchase_request_line(self, purchase_request, procurement):
        return {
            'product_id': procurement.product_id.id,
            'name': procurement.product_id.name,
            'date_required': procurement.date_planned,
            'product_uom_id': procurement.get_mto_qty_to_order(),
            'product_qty': procurement.product_qty,
            'request_id': purchase_request.id,
            'procurement_id': procurement.id
        }
