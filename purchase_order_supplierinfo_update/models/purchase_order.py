# Copyright 2021 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        no_updated = self.filtered(lambda r: r.state not in ["purchase", "done"])
        res = super().write(vals)
        if vals.get("state", "") in ["purchase", "done"]:
            no_updated.mapped("order_line").filtered(
                lambda r: not r.display_type
            ).update_supplierinfo_price()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.update_supplierinfo_price()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("price_unit"):
            self.update_supplierinfo_price()
        return res

    def update_supplierinfo_price(self):
        for line in self.filtered(lambda r: r.order_id.state in ["purchase", "done"]):
            domain = [
                ("partner_id", "=", line.partner_id.id),
                ("product_id", "=", line.product_id.id),
                ("date_order", ">", line.date_order),
            ]
            if not self.env["purchase.order.line"].search(domain, limit=1):
                params = {"order_id": line.order_id}
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                    params=params,
                )
                if seller:
                    line._update_supplierinfo(seller)

    def _update_supplierinfo(self, seller):
        self.ensure_one()
        new_seller_price = self.price_unit
        # convert according to the currency if necessary
        if self.currency_id and self.currency_id != seller.currency_id:
            new_seller_price = self.currency_id._convert(
                new_seller_price,
                seller.currency_id,
                seller.company_id,
                self.date_order or fields.Date.today(),
            )
        # convert according to the UoM if necessary
        if self.product_uom and self.product_uom != seller.product_uom:
            new_seller_price = self.product_uom._compute_price(
                new_seller_price, seller.product_uom
            )
        # Set price
        if new_seller_price != seller.price:
            seller.sudo().price = new_seller_price
