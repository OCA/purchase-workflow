# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange(
        "amount_currency",
        "currency_id",
        "debit",
        "credit",
        "tax_ids",
        "account_id",
        "analytic_account_id",
        "analytic_tag_ids",
    )
    def _onchange_mark_recompute_taxes(self):
        for line in self:
            if line.purchase_line_id.usage_id.account_id:
                account = line.purchase_line_id.usage_id.account_id
            else:
                account = line._get_computed_account()
            line.account_id = account
        return super(AccountMoveLine, self)._onchange_mark_recompute_taxes()
