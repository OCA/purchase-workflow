# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import Command, models


class PurchaseAlternativeCreate(models.TransientModel):
    _inherit = "purchase.alternative.create"

    def _get_alternative_line_value(
        self, order_line, product_tmpl_ids_with_description
    ):
        vals = super()._get_alternative_line_value(
            order_line, product_tmpl_ids_with_description
        )
        if not order_line.purchase_request_lines:
            return vals
        vals["purchase_request_lines"] = [
            Command.set(order_line.purchase_request_lines.ids)
        ]
        vals["purchase_request_allocation_ids"] = [
            Command.create(
                {
                    "purchase_request_line_id": alloc.purchase_request_line_id.id,
                    "requested_product_uom_qty": alloc.requested_product_uom_qty,
                }
            )
            for alloc in order_line.purchase_request_allocation_ids
        ]
        return vals
