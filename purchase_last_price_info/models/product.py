# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_purchase_price = fields.Float(string="Last Purchase Price")
    last_purchase_date = fields.Date(string="Last Purchase Date")
    last_supplier_id = fields.Many2one(
        comodel_name="res.partner", string="Last Supplier"
    )

    def set_product_last_purchase(self, order_id=False):
        """ Get last purchase price, last purchase date and last supplier """
        PurchaseOrderLine = self.env["purchase.order.line"]
        if not self.check_access_rights("write", raise_exception=False):
            return
        for product in self:
            date_order = False
            price_unit_uom = 0.0
            last_supplier = False

            # Check if Order ID was passed, to speed up the search
            if order_id:
                lines = PurchaseOrderLine.search(
                    [("order_id", "=", order_id), ("product_id", "=", product.id)],
                    limit=1,
                )
            else:
                lines = PurchaseOrderLine.search(
                    [
                        ("product_id", "=", product.id),
                        ("state", "in", ["purchase", "done"]),
                    ]
                ).sorted(key=lambda l: l.order_id.date_order, reverse=True)

            if lines:
                # Get most recent Purchase Order Line
                last_line = lines[:1]

                date_order = last_line.order_id.date_order
                # Compute Price Unit in the Product base UoM
                price_unit_uom = product.uom_id._compute_quantity(
                    last_line.price_unit, last_line.product_uom
                )
                last_supplier = last_line.order_id.partner_id

            # Assign values to record
            product.write(
                {
                    "last_purchase_date": date_order,
                    "last_purchase_price": price_unit_uom,
                    "last_supplier_id": last_supplier.id if last_supplier else False,
                }
            )
            # Set related product template values
            product.product_tmpl_id.set_product_template_last_purchase(
                date_order, price_unit_uom, last_supplier
            )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_purchase_price = fields.Float(string="Last Purchase Price")
    last_purchase_date = fields.Date(string="Last Purchase Date")
    last_supplier_id = fields.Many2one(
        comodel_name="res.partner", string="Last Supplier"
    )

    def set_product_template_last_purchase(self, date_order, price_unit, partner_id):
        return self.write(
            {
                "last_purchase_date": date_order,
                "last_purchase_price": price_unit,
                "last_supplier_id": partner_id.id if partner_id else False,
            }
        )
