# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line)
        if (line.usage_id and
                line.product_id.type in ('service', 'consu') and
                line.usage_id.account_id):
            res['account_id'] = line.usage_id.account_id.id
        return res
