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
        cls.product_template = cls.productTemplateObj.create(
            {
                "name": "Product Template",
                "list_price": 100,
                "purchase_ok": True,
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
        color_attribute_line = cls.product_template.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.color_attribute
        )
        products = cls.productVariantObj.search(
            [
                ("product_tmpl_id", "=", cls.product_template.id),
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
        self.assertTrue(self.product_template.purchase_ok)
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

        self.product_template.write({"purchase_ok": False})
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
            "2 rules associated with variants of this template should be removed",
        )

    def test_raiseWarning_unpurchaseable_product(self):
        self.assertTrue(self.product_template.purchase_ok)
        self.product_template.write({"purchase_ok": False})

        with self.assertRaises(UserError):
            self.reorderingRuleObj.create(
                {
                    "product_id": self.product_variant_01.id,
                    "product_min_qty": 10,
                }
            )
