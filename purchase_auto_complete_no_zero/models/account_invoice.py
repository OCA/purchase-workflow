from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        res = super()._onchange_purchase_auto_complete()

        lines_to_keep = self.invoice_line_ids.filtered(
            lambda line: line.display_type in ("line_section", "line_note")
            or (line.quantity > 0 and line.price_unit > 0)
        )

        self.invoice_line_ids = lines_to_keep

        return res
