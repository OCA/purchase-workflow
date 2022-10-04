# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        for orderpoint in self:
            for prline in self.env["purchase.request.line"].search(
                [
                    ("request_id.state", "in", ("draft", "approved", "to_approve")),
                    ("product_id", "=", orderpoint.product_id.id),
                    ("purchase_state", "=", False),
                ]
            ):
                res[orderpoint.id] += prline.product_uom_id._compute_quantity(
                    prline.product_qty, orderpoint.product_uom, round=False
                )
        return res

    @api.depends(
        "product_id.purchase_request_line_ids.product_qty",
        "product_id.purchase_request_line_ids.purchase_state",
        "product_id.purchase_request_line_ids.request_id.state",
        "product_id.purchase_request_line_ids.product_uom_id",
        "product_id.purchase_request_line_ids",
    )
    def _compute_qty(self):
        return super()._compute_qty()
