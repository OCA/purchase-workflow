# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            if not line.purchase_line_id.is_deposit:
                continue
            line.purchase_line_id.taxes_id = line.tax_ids
            line.purchase_line_id.price_unit = line.price_unit
        return res
