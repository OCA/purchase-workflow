# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import SQL


class PurchaseBillLineMatch(models.Model):
    _inherit = "purchase.bill.line.match"

    @property
    def _table_query(self):
        return SQL(
            """
            SELECT * FROM (%s) AS matched
            WHERE matched.pol_id IS NULL
            OR matched.pol_id NOT IN (
                SELECT id
                FROM purchase_order_line
                WHERE force_invoiced
            )
            """,
            super()._table_query,
        )
