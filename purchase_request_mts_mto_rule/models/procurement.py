# -*- coding: utf-8 -*-
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _prepare_purchase_request_line(self, purchase_request, procurement):
        res = super(ProcurementOrder, self)._prepare_purchase_request_line(
            purchase_request, procurement)
        res['product_qty'] = procurement.get_mto_qty_to_order()
        return res
