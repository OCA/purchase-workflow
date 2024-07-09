# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    distribution_bom_id = fields.Many2one("mrp.bom")

    def action_open_distribution_wizard(self):
        return {
            "name": _("Distribution for %s") % self.product_id.display_name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.move.distribution.wiz",
            "target": "new",
            "context": {"active_model": "stock.move", "active_id": self.id},
        }

    def _action_done(self, cancel_backorder=False):
        distribution_moves = self.filtered(lambda m: m.distribution_bom_id)
        new_moves = self.env["stock.move"]
        for move in distribution_moves:
            cancel_move = False
            for sml in move.move_line_ids.filtered(
                lambda ml, move=move: ml.product_id != move.product_id
            ):
                # Create new moves with the corresponding product and the linked sml
                new_moves += self.env["stock.move"].create(
                    {
                        "picking_id": sml.picking_id.id,
                        "product_id": sml.product_id.id,
                        "name": sml.product_id.display_name,
                        "purchase_line_id": move.purchase_line_id.id,
                        "product_uom": sml.product_uom_id.id,
                        "state": "assigned",
                        "location_id": sml.location_id.id,
                        "location_dest_id": sml.location_dest_id.id,
                        "price_unit": move.price_unit,
                        "move_line_ids": [(4, sml.id)],
                    }
                )
                cancel_move = True
            if cancel_move:
                move.state = "cancel"
        return super(StockMove, self + new_moves)._action_done(
            cancel_backorder=cancel_backorder
        )
