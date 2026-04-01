# Copyright (C) 2026  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re

from odoo import fields, models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    last_effective_date = fields.Datetime(readonly=True)

    def _select(self) -> SQL:
        """
        In 'purchase_stock', 'effective_date' is taken from
        'purchase.order' (po). We change it to use
        'purchase.order.line' (l) and add 'last_effective_date'.
        """
        super_select = super()._select()
        # Replace po.effective_date with l.effective_date
        new_select = re.sub(
            r"po\.effective_date", "l.effective_date", super_select.code
        )
        # Add last_effective_date
        new_select += ", l.last_effective_date as last_effective_date"
        return SQL(new_select, *super_select.params)

    def _group_by(self) -> SQL:
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
        super_group_by = super()._group_by()
        # Replace 'effective_date' with 'l.effective_date' in the SQL code.
        # We use a regex to ensure we only replace the exact word 'effective_date'
        # when it's not already qualified.
        new_group_by = re.sub(
            r"(?<!\.)\beffective_date\b", "l.effective_date", super_group_by.code
        )
        new_group_by += ", l.last_effective_date"
        return SQL(new_group_by, *super_group_by.params)
