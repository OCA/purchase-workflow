# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseOrderNoZeroPrice(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.PurchaseOrder = self.env["purchase.order"]
        # Partner
        self.partner1 = self.env.ref("base.res_partner_1")
        # Products
        self.product1 = self.env.ref("product.product_product_7")

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
                            "product_uom": self.product1.uom_id.id,
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

    def test_cannot_confirm_purchase_order_with_zero_price(self):
        self.assertEqual(self.purchase_order2.state, "draft")
        # A zero price is allowed while the PO remains in draft.
        self.purchase_order2.order_line.write({"price_unit": 0.0})
        self.assertEqual(self.purchase_order2.order_line.price_unit, 0.0)
        with self.assertRaises(UserError), self.cr.savepoint():
            self.purchase_order2.button_confirm()
        self.assertEqual(self.purchase_order2.state, "draft")

    def test_cannot_set_zero_price_on_confirmed_purchase_order(self):
        self.purchase_order1.button_confirm()
        self.assertEqual(self.purchase_order1.state, "purchase")
        with self.assertRaises(UserError), self.cr.savepoint():
            self.purchase_order1.order_line.write({"price_unit": 0.0})
        self.assertEqual(self.purchase_order1.order_line.price_unit, 10.0)
