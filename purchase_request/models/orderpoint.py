# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super()._quantity_in_progress()
        # Inventory users may not have access to the requests
        request_lines = self.env["purchase.request.line"].sudo()
        for prline in request_lines.search(
            [
                (
                    "request_id.state",
                    "in",
                    ("draft", "approved", "to_approve", "in_progress"),
                ),
                ("orderpoint_id", "in", self.ids),
                ("purchase_state", "=", False),
            ]
        ):
            res[prline.orderpoint_id.id] += prline.product_uom_id._compute_quantity(
                prline.product_qty, prline.orderpoint_id.uom_id, round=False
            )
        return res
