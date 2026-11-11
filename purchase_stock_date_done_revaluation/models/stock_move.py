# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_purchase_billed(self):
        self.ensure_one()
        if not self.purchase_line_id:
            return False
        return any(
            aml.move_id.state == "posted"
            and aml.move_id.move_type in ("in_invoice", "in_refund")
            for aml in self.purchase_line_id.invoice_lines
        )

    def _is_date_done_revaluation_candidate(self):
        self.ensure_one()
        return (
            self.state == "done"
            and (self.is_in or self.is_dropship)
            and bool(self.purchase_line_id)
            and not self._is_purchase_billed()
        )

    def write(self, vals):
        res = super().write(vals)
        if "date" in vals:
            to_revalue = self.filtered(
                lambda m: m._is_date_done_revaluation_candidate()
            )
            if to_revalue:
                to_revalue._set_value()
        return res
