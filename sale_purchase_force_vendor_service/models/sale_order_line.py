# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _purchase_service_match_supplier(self, warning=True):
        if self.vendor_id and not self.product_id._select_seller(
            partner_id=self.vendor_id,
            quantity=self.product_uom_qty,
            uom_id=self.product_uom_id,
        ):
            self.env["product.supplierinfo"].sudo().create(
                self._prepare_force_vendor_product_supplierinfo_vals()
            )
        return super()._purchase_service_match_supplier(warning=warning)

    def _retrieve_purchase_partner(self):
        return self.vendor_id or super()._retrieve_purchase_partner()
