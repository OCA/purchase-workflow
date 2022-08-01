# Copyright 2019 Alexandre Díaz <alexandre.diaz@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import datetime

from odoo.tests import common


class TestReassign(common.TransactionCase):
    def test_reassign(self):
        vendor = self.env["res.partner"].create(
            {
                "name": "Vendor Test",
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )
        purchase_from = self.env["purchase.order"].create(
            {
                "partner_id": vendor.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "name": "Test Product",
                            "product_id": product.id,
                            "product_qty": 2,
                            "price_unit": 150.00,
                            "date_planned": datetime.now(),
                            "product_uom": self.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )
        purchase_to = self.env["purchase.order"].create(
            {
                "partner_id": vendor.id,
            }
        )
        pl_reassign = (
            self.env["purchase.order.line.reassign.wiz"]
            .with_context(active_ids=purchase_from.order_line.ids)
            .create(
                {
                    "purchase_order_id": purchase_to.id,
                }
            )
        )
        pl_reassign.action_apply()
        self.assertFalse(len(purchase_from.order_line))
        self.assertTrue(len(purchase_to.order_line))
