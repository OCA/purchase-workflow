# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_prepare_order_values(self, supplierinfo):
        result = super()._purchase_service_prepare_order_values(supplierinfo)
        supplier_currency = supplierinfo.partner_id.property_purchase_currency_id
        default_purchase_currency = self.env.company.default_purchase_currency_id
        if not supplier_currency and default_purchase_currency:
            result.update(currency_id=default_purchase_currency.id)
        return result
