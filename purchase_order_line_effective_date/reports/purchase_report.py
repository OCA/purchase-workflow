# Copyright (C) 2026  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re

from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    last_effective_date = fields.Datetime(
        readonly=True,
        help="Completion date of the last receipt order.",
    )

    def _select(self):
        """
        In 'purchase_stock', 'effective_date' is taken from
        'purchase.order' (po). We change it to use
        'purchase.order.line' (l) and add 'last_effective_date'.
        """
        select_str = super()._select()
        # Replace po.effective_date with l.effective_date
        select_str = re.sub(
            r",\s+po\.effective_date\s+as\s+effective_date",
            ", l.effective_date as effective_date",
            select_str,
        )
        # Add last_effective_date
        select_str += ", l.last_effective_date as last_effective_date"
        return select_str

    def _group_by(self):
        """
        The field 'effective_date' is now present in both
        'purchase.order' and 'purchase.order.line'. The 'purchase_stock'
        module adds 'effective_date' (from 'purchase.order') to the
        'GROUP BY' clause of the purchase report without qualifying
        it with the table alias 'po'. This causes an 'AmbiguousColumn'
        error because the report also joins 'purchase.order.line' as 'l'.

        We fix this by qualifying 'effective_date' with 'l' instead of 'po' and
        adding 'last_effective_date'.
        """
        group_by_str = super()._group_by()
        # Replace 'effective_date' with 'l.effective_date' in the SQL code.
        # We use a regex to ensure we only replace the exact word 'effective_date'
        # when it's not already qualified.
        group_by_str = re.sub(
            r"(?<!\.)\beffective_date\b",
            "l.effective_date",
            group_by_str,
        )
        group_by_str += ", l.last_effective_date"
        return group_by_str
