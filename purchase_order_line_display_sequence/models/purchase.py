# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
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

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(PurchaseOrder, self.with_context(keep_line_sequence=True)).copy(
            default
        )
