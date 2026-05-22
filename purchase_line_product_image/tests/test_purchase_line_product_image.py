# Copyright 2017 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# Copyright 2026 TesseraTech Solutions S.L. <https://www.tesseratech.es>
# Copyright 2026 Paco Montés <f.montesdoria@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import fields

from odoo.addons.base.tests.common import TransactionCase

# Minimal valid 1x1 GIF image
GIF_1X1 = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    b"\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
    b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)


class TestPurchaseLineProductImage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "image_1920": base64.b64encode(GIF_1X1),
            }
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.display_name,
                            "product_id": cls.product.id,
                            "product_qty": 1.0,
                            "product_uom": cls.product.uom_po_id.id,
                            "price_unit": 10.0,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        cls.purchase_line = cls.purchase.order_line

    def test_purchase_line_product_image_related(self):
        self.assertTrue(self.product.image_128)
        self.assertEqual(self.purchase_line.product_id, self.product)
        self.assertEqual(self.purchase_line.product_image, self.product.image_128)
