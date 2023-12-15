# Copyright 2023 Jarsa, (<https://www.jarsa.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_purchase_description(self, product_lang):
        name = super()._get_product_purchase_description(product_lang)
        if self.product_id.default_code:
            name = name.replace(f"[{self.product_id.default_code}] ", "").strip()
        return name
