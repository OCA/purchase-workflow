# Copyright 2020 Jarsa Sistemas
# Copyright 2021 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_secondary_uom_for_move(self, product_uom_qty):
        if not self.secondary_uom_id:
            return 0.0
        move = self.env["stock.move"].new()
        move.product_id = self.product_id
        move.product_uom = self.product_uom
        move.secondary_uom_id = self.secondary_uom_id
        move.product_uom_qty = product_uom_qty
        return move.secondary_uom_qty

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        # Ensure one method.
        # Compute secondary unit values for stock moves.
        # When a po line with stock moves has been updated the new moves only
        # have the new quantity added so we always want compute the
        # secondary unit.
        if res:
            product_uom_qty = res[0]["product_uom_qty"]
            secondary_uom_qty = self._get_secondary_uom_for_move(product_uom_qty)
            res[0].update(
                {
                    "secondary_uom_id": self.secondary_uom_id.id,
                    "secondary_uom_qty": secondary_uom_qty,
                }
            )
        return res

    def _create_or_update_picking(self):
        # Inject a context to recompute secondary unit in stock moves after
        # they have been assigned only for po lines updated and confirmed.
        return super(
            PurchaseOrderLine, self.with_context(secondary_uom_for_update_moves=True)
        )._create_or_update_picking()
