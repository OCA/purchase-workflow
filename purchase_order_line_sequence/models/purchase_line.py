# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _order = "sequence, id"

    sequence = fields.Integer(
        "Hidden Sequence",
        help="Gives the sequence of the line when " "displaying the purchase order.",
        default=9999,
    )

    visible_sequence = fields.Integer(
        "Line Number",
        help="Displays the sequence of the line in the purchase order.",
        compute="_compute_visible_sequence",
        store=True,
    )

    @api.depends("sequence", "order_id.order_line")
    def _compute_visible_sequence(self):
        for po in self.mapped("order_id"):
            sequence = 1
            order_lines = po.order_line.filtered(lambda pol: not pol.display_type)
            for line in sorted(order_lines, key=lambda pol: pol.sequence):
                line.visible_sequence = sequence
                sequence += 1
