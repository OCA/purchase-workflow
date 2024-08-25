# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):

    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        return {
            "product_packaging_id": item.line_id.product_packaging_id.id,
            **super()._prepare_purchase_order_line(po, item),
        }

    @api.model
    def _get_order_line_search_domain(self, order, item):
        return [
            ("product_packaging_id", "=", item.line_id.product_packaging_id.id),
            *super()._get_order_line_search_domain(order, item),
        ]
