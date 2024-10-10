# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "move_ids.state",
        "move_ids.product_uom",
        "move_ids.product_uom_qty",
        "product_qty",
        "qty_received",
    )
    def _compute_qty_to_receive(self):
        """Compute the quantity for which there are pending stock moves"""
        service_lines = self.filtered(lambda line: line.product_id.type == "service")
        for line in self - service_lines:
            total = 0.0
            for move in line.move_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            ):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom
                    )
                else:
                    total += move.product_uom_qty
            line.qty_to_receive = total
        for line in service_lines:
            line.qty_to_receive = line.product_qty - line.qty_received

    qty_to_receive = fields.Float(
        compute="_compute_qty_to_receive",
        digits="Product Unit of Measure",
        copy=False,
        string="Qty to Receive",
        store=True,
    )
