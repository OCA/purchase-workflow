# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _amend_and_reprocure(self):
        """
            Filter lines that can reprocure.
            Try to find purchase line with move destination linked to the sale
            order.
            The purchase order should be draft. Cancelled lines are ignored
        """
        lines = self.filtered("can_amend_and_reprocure")
        moves = lines.mapped("move_ids") | lines.mapped("move_ids.move_orig_ids")
        po_lines = self.env["purchase.order.line"].search(
            [("move_dest_ids", "in", moves.ids), ("state", "!=", "cancel")]
        )
        if any(po_line.state != "draft" for po_line in po_lines):
            raise ValidationError(
                _(
                    "You cannot modify a sale order line linked to a"
                    "confirmed purchase order!"
                )
            )
        po_lines.unlink()
        return super()._amend_and_reprocure()
