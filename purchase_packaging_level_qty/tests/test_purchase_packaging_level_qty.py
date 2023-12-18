# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchasePackagingLevel(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.level1 = cls.env["product.packaging.level"].create(
            {
                "name": "Packaging Level 1 Test",
                "code": "Pack1",
                "sequence": 2,
            }
        )
        cls.level2 = cls.env["product.packaging.level"].create(
            {
                "name": "Packaging Level 2 Test",
                "code": "Pack2",
                "sequence": 3,
            }
        )
        cls.packaging1 = cls.env["product.packaging"].create(
            {"name": "Packaging Test 1", "packaging_level_id": cls.level1.id, "qty": 4}
        )
        cls.packaging2 = cls.env["product.packaging"].create(
            {"name": "Packaging Test 2", "packaging_level_id": cls.level2.id, "qty": 2}
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "packaging_ids": [(6, 0, (cls.packaging1 | cls.packaging2).ids)],
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product Test2",
            }
        )

        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
            }
        )

        cls.config = cls.env["res.config.settings"].create({})
        cls.config.purchase_packaging_level_id = cls.level1
        cls.config.set_values()

    def test_purchase_transport_packaging_level_enabled(self):
        self.config.purchase_packaging_level_id = False
        self.config.set_values()
        self.assertEqual(self.purchase_order.total_transport_qty, False)

    def test_purchase_packaging_level_qty(self):
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product2.name,
                "product_id": self.product2.id,
                "product_qty": 1,
            }
        )
        self.assertEqual(
            self.purchase_order.total_transport_qty, "0.0 Packaging Level 1 Test"
        )

        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 1,
            }
        )
        self.assertEqual(self.purchase_order.order_line[1].transport_qty, 0.25)
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 4,
            }
        )
        self.assertEqual(self.purchase_order.order_line[2].transport_qty, 1)
        self.env["purchase.order.line"].create(
            {
                "order_id": self.purchase_order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_qty": 8,
            }
        )
        self.assertEqual(self.purchase_order.order_line[3].transport_qty, 2)
        self.assertEqual(
            self.purchase_order.total_transport_qty, "3.25 Packaging Level 1 Test"
        )
