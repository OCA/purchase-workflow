# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.exceptions import UserError
from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrderNoZeroPrice(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.PurchaseOrder = self.env["purchase.order"]
        # Partner
        self.partner1 = self.env["res.partner"].create({"name": "Test Partner"})
        # Products
        self.product1 = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "standard_price": 10.0,
            }
        )

        self.purchase_order1 = self.PurchaseOrder.create(
            {
                "partner_id": self.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product1.name,
                            "product_id": self.product1.id,
                            "product_qty": 50,
                            "product_uom_id": self.product1.uom_id.id,
                            "price_unit": 10.0,
                            "date_planned": time.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        },
                    )
                ],
            }
        )
        self.purchase_order2 = self.purchase_order1.copy()

    def test_check_price_unit_zero(self):
        self.assertEqual(self.purchase_order1.state, "draft")
        self.purchase_order1.button_confirm()
        self.assertEqual(self.purchase_order1.state, "purchase")

        self.assertEqual(self.purchase_order2.state, "draft")
        with self.assertRaises(UserError), self.cr.savepoint():
            self.purchase_order2.order_line.write({"price_unit": 0.0})
            self.purchase_order2.button_confirm()
        self.assertEqual(self.purchase_order2.state, "draft")
