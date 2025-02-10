# Copyright 2021-2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    proposed_qty = fields.Float(
        compute="_compute_proposed_qty", store=True, digits="Product Unit of Measure"
    )

    @api.depends(
        "requisition_id.purchase_ids",
        "requisition_id.purchase_ids.order_line",
        "requisition_id.purchase_ids.order_line.product_id",
        "requisition_id.purchase_ids.order_line.product_qty",
        "requisition_id.purchase_ids.state",
    )
    def _compute_proposed_qty(self):
        for item in self:
            item.proposed_qty = sum(
                item.requisition_id.purchase_ids.filtered(
                    lambda x: x.state not in ("cancel")
                )
                .order_line.filtered(
                    lambda x, item=item: x.product_id == item.product_id
                )
                .mapped("product_qty")
            )

    def _prepare_purchase_order_line(
        self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False
    ):
        if self.requisition_id.is_quantity_copy == "remaining_qty":
            product_qty = self.product_qty - self.proposed_qty
        return super()._prepare_purchase_order_line(
            name=name,
            product_qty=product_qty,
            price_unit=price_unit,
            taxes_ids=taxes_ids,
        )
