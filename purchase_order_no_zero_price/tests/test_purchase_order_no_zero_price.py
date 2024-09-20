# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestPurchaseOrderNoZeroPrice(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.PurchaseOrder = cls.env["purchase.order"]
        # Partner
        cls.partner1 = cls.env.ref("base.res_partner_1")
        # Products
        cls.product1 = cls.env.ref("product.product_product_7")

        cls.purchase_order1 = cls.PurchaseOrder.create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product1.name,
                            "product_id": cls.product1.id,
                            "product_qty": 50,
                            "product_uom": cls.product1.uom_id.id,
                            "price_unit": 10.0,
                            "date_planned": time.strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        },
                    )
                ],
            }
        )
        cls.purchase_order2 = cls.purchase_order1.copy()

    def test_check_price_unit_zero(self):
        self.assertEqual(self.purchase_order1.state, "draft")
        self.purchase_order1.button_confirm()
        self.assertEqual(self.purchase_order1.state, "purchase")

        self.assertEqual(self.purchase_order2.state, "draft")
        with self.assertRaises(UserError), self.cr.savepoint():
            self.purchase_order2.order_line.write({"price_unit": 0.0})
            self.purchase_order2.button_confirm()
        self.assertEqual(self.purchase_order2.state, "draft")
