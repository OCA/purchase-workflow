# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            if not line.purchase_line_id.is_deposit:
                continue
            order = line.purchase_line_id.order_id
            line.purchase_line_id.tax_ids = line.tax_ids
            # The bill may be issued in a currency other than the order one.
            line.purchase_line_id.price_unit = line.currency_id._convert(
                line.price_unit,
                order.currency_id,
                order.company_id,
                line.move_id.invoice_date or fields.Date.context_today(self),
                round=False,
            )
        return res
