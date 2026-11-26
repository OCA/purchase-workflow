# Copyright 2026 Marcos Mendez <m@pop.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("last_purchase_price", "Last Purchase Price")],
        ondelete={"last_purchase_price": "set default"},
    )

    def _get_price_label_base_str(self):
        if self.base == "last_purchase_price":
            return self.env._("last purchase price")
        return super()._get_price_label_base_str()

    def _compute_base_price(self, product, quantity, uom, date, currency):
        if self.base != "last_purchase_price":
            return super()._compute_base_price(product, quantity, uom, date, currency)
        line = self._get_last_purchase_line(product)
        if not line:
            # Never bought: fall back to the product cost, as the core
            # "Cost" base does.
            price = product._price_compute("standard_price", uom=uom, date=date)[
                product.id
            ]
            return product.cost_currency_id._convert(
                price, currency, self.env.company, date, round=False
            )
        price = line.price_unit_discounted
        target_uom = uom or product.uom_id
        if line.product_uom != target_uom:
            price = line.product_uom._compute_price(price, target_uom)
        if line.currency_id != currency:
            price = line.currency_id._convert(
                price, currency, line.company_id, date, round=False
            )
        return price

    def _get_last_purchase_line(self, product):
        """Last confirmed purchase line of the product (or of any variant of
        the template) made by the company of the pricelist, or by the current
        company when the pricelist is shared."""
        variants = (
            product.product_variant_ids
            if product._name == "product.template"
            else product
        )
        company = self.pricelist_id.company_id or self.env.company
        return (
            self.env["purchase.order.line"]
            .sudo()
            .search(
                [
                    ("product_id", "in", variants.ids),
                    ("state", "in", ["purchase", "done"]),
                    ("company_id", "=", company.id),
                ],
                order="date_order desc, id desc",
                limit=1,
            )
        )
