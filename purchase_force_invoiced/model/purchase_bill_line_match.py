# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

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
                SELECT pol.id
                FROM purchase_order_line pol
                    JOIN purchase_order po ON pol.order_id = po.id
                WHERE po.force_invoiced
            )
            """,
            super()._table_query,
        )
