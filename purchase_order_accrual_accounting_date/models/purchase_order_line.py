# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_invoice_lines(self):
        # Use the accounting date of the bill instead of its bill date, when
        # the company enables it.
        self.ensure_one()
        accrual_date = self.env.context.get("accrual_entry_date")
        if not accrual_date or not self.company_id.accrual_use_accounting_date:
            return super()._get_invoice_lines()
        return self.invoice_lines.filtered(
            lambda line: line.move_id.date and line.move_id.date <= accrual_date
        )
