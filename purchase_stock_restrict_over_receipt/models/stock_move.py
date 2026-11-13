# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import formatLang


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_purchase_unordered_product(self):
        """Refuse a product received on a purchase receipt without being ordered."""
        unordered = self.filtered(
            lambda move: not move.purchase_line_id
            and move.product_id not in move.picking_id.purchase_id.order_line.product_id
        )
        if not unordered:
            return
        details = "\n".join(
            self.env._(
                "- %(order)s: %(product)s",
                order=move.picking_id.purchase_id.name,
                product=move.product_id.display_name,
            )
            for move in unordered
        )
        raise UserError(
            self.env._(
                "You cannot receive a product that is not on the purchase order.\n"
                "%(details)s\n"
                "Update the purchase order first.",
                details=details,
            )
        )

    def _check_purchase_over_receipt(self):
        """Refuse a receipt that leaves an order line received beyond its order."""
        over_lines = self.purchase_line_id.filtered(
            lambda line: line.product_uom_id.compare(
                line.qty_received, line.product_qty
            )
            > 0
        )
        if not over_lines:
            return
        details = "\n".join(
            self.env._(
                "- %(order)s, %(product)s: %(received)s %(uom)s received in total, "
                "%(ordered)s %(uom)s ordered",
                order=line.order_id.name,
                product=line.product_id.display_name,
                received=formatLang(self.env, line.qty_received, dp="Product Unit"),
                ordered=formatLang(self.env, line.product_qty, dp="Product Unit"),
                uom=line.product_uom_id.name,
            )
            for line in over_lines
        )
        raise UserError(
            self.env._(
                "You cannot receive more than the quantity ordered.\n"
                "%(details)s\n"
                "Update the purchase order first.",
                details=details,
            )
        )

    def _action_synch_order(self):
        # Moves from the vendor only, as in purchase_stock: a return must stay
        # possible on a line that is already over received.
        receipts = self.filtered(
            lambda move: move.picking_id.purchase_id
            and move.location_id.usage in ("supplier", "transit")
        )
        # Checked before super(), which adds an order line for such a product:
        # a user without purchase rights would get an access error instead.
        receipts._check_purchase_unordered_product()
        res = super()._action_synch_order()
        receipts._check_purchase_over_receipt()
        return res
