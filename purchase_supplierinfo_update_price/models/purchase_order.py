# Copyright 2021 Open Source Intergrators (<http://opensourceintegrators.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _update_supplierinfo(self):
        for order in self:
            partner = (
                order.partner_id
                if not order.partner_id.parent_id
                else order.partner_id.parent_id
            )
            for line in order.order_line.filtered("product_id").filtered("price_unit"):
                product = line.product_id
                all_supplierinfo = product.seller_ids.filtered(
                    lambda x: x.name == partner and line.product_qty >= x.min_qty
                )
                supplierinfo = all_supplierinfo[-1:]
                if supplierinfo and supplierinfo.price != line.price_unit:
                    supplierinfo.price = line.price_unit

    def action_create_invoice(self):
        self._update_supplierinfo()
        return super().action_create_invoice()
