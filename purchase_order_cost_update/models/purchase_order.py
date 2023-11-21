# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_view_update_standard_price_wizard(self):
        self.mapped("order_line").update_supplierinfo_price()
        self.mapped("order_line").update_product_standard_price()



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def update_product_standard_price(self):
        for line in self:
            new_seller_price = line.price_unit
            line.product_id.standard_price = new_seller_price
