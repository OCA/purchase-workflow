# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "base.cancel.confirm"]

    _has_cancel_reason = "optional"  # ["no", "optional", "required"]

    cancel_confirm = fields.Boolean(default=False, copy=False)

    def button_cancel(self):
        if self.env.context.get("cancel_confirm_wizard") and not self.filtered(
            "cancel_confirm"
        ):
            return self.open_cancel_confirm_wizard()
        return super().button_cancel()

    def button_draft(self):
        self.clear_cancel_confirm_data()
        return super().button_draft()
