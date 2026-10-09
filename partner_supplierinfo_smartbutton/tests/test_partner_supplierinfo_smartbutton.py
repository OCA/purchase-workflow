# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestPartnerSupplierinfoSmartbutton(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env["res.partner"].create({"name": "Partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Partner B"})
        cls.partner_c = cls.env["res.partner"].create({"name": "Partner C"})
        cls.product_model = cls.env["product.product"]
        cls.product_supplierinfo_model = cls.env["product.supplierinfo"]
        cls.product_a = cls.product_model.create(
            {
                "name": "Test product A",
                "seller_ids": [
                    (
                        0,
                        False,
                        {"partner_id": cls.partner_a.id, "min_qty": 1, "price": 10},
                    ),
                ],
            }
        )
        cls.product_b = cls.product_model.create(
            {
                "name": "Test product B",
                "seller_ids": [
                    (
                        0,
                        False,
                        {"partner_id": cls.partner_b.id, "min_qty": 1, "price": 10},
                    ),
                ],
            }
        )
        cls.product_a_b = cls.product_model.create(
            {
                "name": "Test product A+B",
                "seller_ids": [
                    (
                        0,
                        False,
                        {"partner_id": cls.partner_a.id, "min_qty": 1, "price": 10},
                    ),
                    (
                        0,
                        False,
                        {"partner_id": cls.partner_b.id, "min_qty": 1, "price": 20},
                    ),
                ],
            }
        )
        cls.product_c = cls.product_model.create({"name": "Test product C"})

    def _get_products_from_action(self, action):
        return self.product_supplierinfo_model.search(action["domain"]).mapped(
            "product_tmpl_id"
        )

    def test_product_supplied_count(self):
        # Partner A
        products = self._get_products_from_action(
            self.partner_a.action_see_products_by_seller()
        )
        self.assertIn(self.product_a.product_tmpl_id, products)
        self.assertNotIn(self.product_b.product_tmpl_id, products)
        self.assertIn(self.product_a_b.product_tmpl_id, products)
        self.assertNotIn(self.product_c.product_tmpl_id, products)
        self.assertEqual(self.partner_a.product_supplied_count, 2)
        # Partner B
        products = self._get_products_from_action(
            self.partner_b.action_see_products_by_seller()
        )
        self.assertNotIn(self.product_a.product_tmpl_id, products)
        self.assertIn(self.product_b.product_tmpl_id, products)
        self.assertIn(self.product_a_b.product_tmpl_id, products)
        self.assertNotIn(self.product_c.product_tmpl_id, products)
        self.assertEqual(self.partner_b.product_supplied_count, 2)
        # Partner C
        products = self._get_products_from_action(
            self.partner_c.action_see_products_by_seller()
        )
        self.assertNotIn(self.product_a.product_tmpl_id, products)
        self.assertNotIn(self.product_b.product_tmpl_id, products)
        self.assertNotIn(self.product_a_b.product_tmpl_id, products)
        self.assertNotIn(self.product_c.product_tmpl_id, products)
        self.assertEqual(self.partner_c.product_supplied_count, 0)
