# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.fields import Command

from odoo.addons.product.tests.common import ProductAttributesCommon


class TestUnpurchaseableProduct(ProductAttributesCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.productTemplateObj = cls.env["product.template"]
        cls.productVariantObj = cls.env["product.product"]
        cls.reorderingRuleObj = cls.env["stock.warehouse.orderpoint"]
        cls.product_template_01 = cls.productTemplateObj.create(
            {
                "name": "Product Template 01",
                "list_price": 100,
                "purchase_ok": True,
                "type": "product",
                "attribute_line_ids": [
                    Command.create(
                        {  # two variants for this one
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [
                                Command.link(cls.color_attribute_red.id),
                                Command.link(cls.color_attribute_blue.id),
                            ],
                        }
                    ),
                ],
            }
        )
        cls.product_template_02 = cls.productTemplateObj.create(
            {
                "name": "Product Template 02",
                "list_price": 100,
                "purchase_ok": False,
                "type": "product",
            }
        )
        color_attribute_line = cls.product_template_01.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.color_attribute
        )
        products = cls.productVariantObj.search(
            [
                ("product_tmpl_id", "=", cls.product_template_01.id),
                (
                    "product_template_attribute_value_ids",
                    "in",
                    color_attribute_line.product_template_value_ids.ids,
                ),
            ]
        )
        cls.product_variant_01 = products[0]
        cls.product_variant_02 = products[1]
        cls.rule_product_variant_01 = cls.reorderingRuleObj.create(
            {
                "product_id": cls.product_variant_01.id,
                "product_min_qty": 10,
            }
        )
        cls.rule_product_variant_02 = cls.reorderingRuleObj.create(
            {
                "product_id": cls.product_variant_02.id,
                "product_min_qty": 20,
            }
        )

    def test_unpurchaseable_product_template(self):
        self.assertTrue(self.product_template_01.purchase_ok)
        rules = self.reorderingRuleObj.search(
            [
                (
                    "product_id",
                    "in",
                    [self.product_variant_01.id, self.product_variant_02.id],
                )
            ]
        )
        self.assertEqual(len(rules), 2)

        self.product_template_01.write({"purchase_ok": False})
        rules = self.reorderingRuleObj.search(
            [
                (
                    "product_id",
                    "in",
                    [self.product_variant_01.id, self.product_variant_02.id],
                )
            ]
        )
        self.assertEqual(
            len(rules),
            0,
            "2 rules associated with variants of this template should be archived",
        )

    def test_get_orderpoint_products(self):
        # Cleanup existing rules
        self.env["stock.warehouse.orderpoint"].search([]).unlink()

        # Order point is created when there is moves linked with the product
        self.env["stock.move"].create(
            {
                "company_id": self.env.company.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product_variant_01.id,
                "product_uom": self.product_variant_01.uom_id.id,
                "name": "stock_move",
            }
        )
        products = self.env["stock.warehouse.orderpoint"]._get_orderpoint_products()
        self.assertIn(self.product_variant_01, products)

        # Excluding unpurchaseable
        self.product_template_01.write({"purchase_ok": False})
        products = self.env["stock.warehouse.orderpoint"]._get_orderpoint_products()
        self.assertNotIn(self.product_variant_01, products)

    def test_raiseWarning_unpurchaseable_product(self):
        self.assertFalse(self.product_template_02.purchase_ok)
        with self.assertRaises(UserError):
            self.reorderingRuleObj.create(
                {
                    "product_id": self.product_template_02.product_variant_id.id,
                    "product_min_qty": 10,
                }
            )
