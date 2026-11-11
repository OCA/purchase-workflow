# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.update_supplierinfo_price()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("price_unit") or vals.get("discount"):
            self.update_supplierinfo_price()
        return res

    def update_supplierinfo_price(self):
        for rec in self.filtered(
            lambda x: not x.display_type and x.order_id.state in ["purchase", "done"]
        ):
            domain = [
                ("partner_id", "=", rec.partner_id.id),
                ("product_id", "=", rec.product_id.id),
                ("date_order", ">", rec.date_order),
            ]
            if not self.env["purchase.order.line"].search_count(domain, limit=1):
                params = {"order_id": rec.order_id}
                seller = rec.product_id._select_seller(
                    partner_id=rec.partner_id,
                    quantity=rec.product_qty,
                    date=rec.order_id.date_order and rec.order_id.date_order.date(),
                    uom_id=rec.uom_id,
                    params=params,
                )
                if seller := seller.get("supplierinfo", False):
                    rec._update_supplierinfo(seller=seller)

    def _update_supplierinfo(self, seller):
        self.ensure_one()
        new_seller_price = self.price_unit
        # convert according to the currency if necessary
        if self.currency_id and self.currency_id != seller.currency_id:
            new_seller_price = self.currency_id._convert(
                from_amount=new_seller_price,
                to_currency=seller.currency_id,
                company=seller.company_id,
                date=self.date_order or fields.Date.today(),
            )
        # convert according to the UoM if necessary
        if self.uom_id and self.uom_id != seller.uom_id:
            new_seller_price = self.uom_id._compute_price(
                price=new_seller_price,
                to_unit=seller.uom_id,
            )
        # Set price
        if new_seller_price != seller.price:
            seller.sudo().price = new_seller_price
        if self.discount != seller.discount:
            seller.sudo().discount = self.discount
