# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        res = super()._create_picking()
        self._update_moves_sequence()
        return res

    def _update_moves_sequence(self):
        for order in self:
            if any(
                [
                    ptype == "consu"
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                for picking in order.picking_ids:
                    for move in picking.move_ids:
                        if not move.purchase_line_id:
                            continue
                        move.write({"sequence": move.purchase_line_id.visible_sequence})

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._update_moves_sequence()
        return res

    def write(self, line_values):
        res = super().write(line_values)
        if "order_line" in line_values:
            self._update_moves_sequence()
        return res
