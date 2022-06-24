# Copyright 2022 elego Software Solutions, Germany (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        if line.product_id.must_have_dates:
            data.update(
                {
                    "start_date": line.start_date,
                    "end_date": line.end_date,
                }
            )
        return data
