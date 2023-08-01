# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends("order_line")
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in purchase order lines.
        Then we add 1 to this value for the next sequence which is given
        to the context of the o2m field in the view. So when we create a new
        purchase order line, the sequence is automatically max_sequence + 1
        """
        for purchase in self:
            purchase.max_line_sequence = (
                max(purchase.mapped("order_line.sequence") or [0]) + 1
            )

    max_line_sequence = fields.Integer(
        string="Max sequence in lines", compute="_compute_max_line_sequence"
    )

    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()
        self._update_moves_sequence()
        return res

    def _update_moves_sequence(self):
        for order in self:
            if any(
                [
                    ptype in ["product", "consu"]
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
        res = super(PurchaseOrder, self).create(vals_list)
        self._update_moves_sequence()
        return res

    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        if "order_line" in line_values:
            self._update_moves_sequence()
        return res
