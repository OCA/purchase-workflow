# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrderLineSellerUsed(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.purchase_model = cls.env["purchase.order"]
        cls.purchase_line_model = cls.env["purchase.order.line"]
        cls.product_supplierinfo_model = cls.env["product.supplierinfo"]

        # Existing instances
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product = cls.env.ref("product.product_product_6")

    @classmethod
    def _create_seller(cls, product, vendor, min_qty=1.0, price=100.0):
        vals = {
            "name": vendor.id,
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_id": product.id,
            "min_qty": min_qty,
            "price": price,
        }
        return cls.product_supplierinfo_model.create(vals)

    @classmethod
    def _create_po(cls, vendor, product, product_qty):
        vals = {
            "partner_id": vendor.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_qty": product_qty,
                        "price_unit": 0.0,
                        "product_uom": product.product_tmpl_id.uom_id.id,
                        "date_planned": fields.Date.today(),
                    },
                ),
            ],
        }
        return cls.purchase_model.create(vals)

    def test_01_check_seller_used_updated(self):
        """
        Check that the Vendor Pricelist used is correctly updated every time
        the Product Quantity changes on the PO line.
        """
        seller_1 = self._create_seller(
            self.product, self.partner, min_qty=20.0, price=100.0
        )
        seller_2 = self._create_seller(
            self.product, self.partner, min_qty=1.0, price=200.0
        )
        purchase = self._create_po(self.partner, self.product, 20.0)
        purchase_line = purchase.order_line
        self.assertEqual(
            len(purchase_line), 1, "It should only be one Purchase Order Line created."
        )
        self.assertEqual(
            purchase_line.seller_used_id,
            seller_1,
            "The Seller Used should be the Seller 1.",
        )
        purchase_line.write({"product_qty": 1.0})
        self.assertEqual(
            purchase_line.seller_used_id,
            seller_2,
            "The Seller Used should now have changed to Seller 2.",
        )
