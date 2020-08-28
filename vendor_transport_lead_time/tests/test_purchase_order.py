# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests.common import Form, SavepointCase


class TestPurchaseOrderDelay(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.vendor = cls.env["res.partner"].create({"name": "vendor1"})
        cls.product_consu = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.vendor.id,
                            "min_qty": 1,
                            "price": 10,
                            "supplier_delay": 6,
                            "transport_delay": 4,
                        },
                    )
                ],
            }
        )

    def test_supplier_date_planned(self):
        po = Form(self.env["purchase.order"])
        po.partner_id = self.vendor
        po.date_order = "2020-08-10"
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_consu
            po_line.product_qty = 1
            self.assertEqual(po_line.price_unit, 10)
            self.assertEqual(fields.Date.to_string(po_line.date_planned), "2020-08-20")
            self.assertEqual(
                fields.Date.to_string(po_line.supplier_date_planned), "2020-08-16"
            )
