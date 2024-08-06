# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    manually_generated = fields.Boolean()

    manually_received_qty = fields.Float(
        compute="_compute_manually_received_qty",
        digits="Product Unit of Measure",
        help="Qty that has been received for stock move (in product's" " PO UoM)",
        store=True,
    )

    @api.depends(
        "manually_generated",
        "product_uom_qty",
        "product_uom",
        "product_id.uom_po_id",
    )
    def _compute_manually_received_qty(self):
        for move in self:
            if not move.manually_generated:
                move.manually_received_qty = 0
            else:
                from_uom = move.product_uom
                to_uom = move.product_id.uom_po_id
                qty = move.product_uom_qty
                move.manually_received_qty = from_uom._compute_quantity(
                    qty, to_uom, round=False
                )
