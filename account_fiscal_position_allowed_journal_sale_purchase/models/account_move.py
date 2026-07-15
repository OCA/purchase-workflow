# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_fiscal_position_id(self):
        """When both sale and purchase are installed, the fiscal position is
        recomputed from the partner whenever a related field changes, which
        would override the one set on the originating purchase order. Keep the
        purchase order's fiscal position on the related vendor bill.
        """
        res = super()._compute_fiscal_position_id()
        for move in self:
            purchase_order = move.line_ids.purchase_line_id.order_id[:1]
            if purchase_order.fiscal_position_id:
                move.fiscal_position_id = purchase_order.fiscal_position_id
        return res
