# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm_manual(self):
        return super(
            PurchaseOrder, self.with_context(manual_delivery=True)
        ).button_confirm()
