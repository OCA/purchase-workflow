# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
# Copyright 2022 Tecnativa - Pedro M. Baeza
import logging

from odoo import models
from odoo.tools import SQL

_logger = logging.getLogger(__name__)


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    def _select(self):
        """Put quantity to be billed as 0 if it has been forced."""
        select_sql = super()._select()
        old = "case when t.purchase_method = 'purchase'"
        new = (
            "case when po.force_invoiced then 0.0 "
            "when t.purchase_method = 'purchase'"
        )
        code = select_sql.code.replace(old, new)
        if "force_invoiced" not in code:
            _logger.error(
                "Query substitution failed. Check 'purchase/report/purchase_report.py "
                "for changes"
            )
        return SQL(code, *select_sql.params)
