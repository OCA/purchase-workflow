# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
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

    sequence2 = fields.Integer(
        "Sequence",
        help="Displays the sequence of the line in " "the purchase order.",
        related="sequence",
        readonly=True,
    )

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        # We do not reset the sequence when copying an entire purchase order
        if not self.env.context.get("keep_line_sequence"):
            line.order_id._reset_sequence()
        return line
