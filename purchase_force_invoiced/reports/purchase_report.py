# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
# Copyright 2022 Tecnativa - Pedro M. Baeza

from odoo import models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    def _select(self):
        """Put quantity to be billed as 0 if it has been forced."""
        select_str = super()._select()
        select_str = select_str.replace(
            "case when t.purchase_method = 'purchase'",
            "case when po.force_invoiced then 0.0 "
            "else (case when t.purchase_method = 'purchase' ",
        )
        select_str = select_str.replace(
            "end as qty_to_be_billed", "end) end as qty_to_be_billed"
        )
        return select_str
