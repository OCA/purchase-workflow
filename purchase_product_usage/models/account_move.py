# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _onchange_mark_recompute_taxes(self):
        for line in self:
            if line.purchase_line_id.usage_id.account_id:
                account = line.purchase_line_id.usage_id.account_id
            else:
                account = line._get_computed_account()
            line.account_id = account
        return super(AccountMoveLine, self)._onchange_mark_recompute_taxes()
