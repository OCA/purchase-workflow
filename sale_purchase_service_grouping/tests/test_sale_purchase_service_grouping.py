# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSalePurchaseServiceGrouping(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        module = "sale_purchase_service_grouping"
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.supplier = cls.env.ref("{}.res_partner_supplier".format(module))
        cls.category = cls.env.ref("{}.product_category".format(module))
        cls.product_a_1 = cls.env.ref("{}.product_a_1".format(module))
        cls.product_a_2 = cls.env.ref("{}.product_a_2".format(module))
        cls.product_b = cls.env.ref("{}.product_b".format(module))

    def _search_purchases(self):
        return self.env["purchase.order"].search(
            [("partner_id", "=", self.supplier.id)]
        )

    def _create_sale_order(self, product_qty, **vals):
        order_vals = {
            "partner_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_qty": qty,
                    }
                )
                for product, qty in product_qty
            ],
        }
        if vals:
            order_vals.update(vals)
        return self.env["sale.order"].create(order_vals)

    def test_purchase_service_group_by_category_grouped(self):
        self.category.purchase_service_grouping = "product.category"
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 1)

    def test_purchase_service_group_by_category_ungrouped(self):
        self.category.purchase_service_grouping = "product.category"
        category_c = self.category.copy({"name": "New Categ"})
        self.product_b.categ_id = category_c
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 2)

    def test_purchase_service_group_by_template(self):
        self.category.purchase_service_grouping = "product.template"
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_2, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 2)

    def test_purchase_service_group_by_product(self):
        self.category.purchase_service_grouping = "product"
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_2, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 3)

    def test_purchase_service_group_by_order_ungrouped(self):
        self.category.purchase_service_grouping = "sale.order"
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_2, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 3)

    def test_purchase_service_group_by_order_grouped(self):
        self._create_sale_order(
            [
                (self.product_b, 1),
                (self.product_a_1, 1),
                (self.product_a_2, 1),
            ]
        ).action_confirm()
        self.assertEqual(len(self._search_purchases()), 1)

    def test_purchase_service_group_default(self):
        self.category.purchase_service_grouping = False
        self._create_sale_order([(self.product_b, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_1, 1)]).action_confirm()
        self._create_sale_order([(self.product_a_2, 1)]).action_confirm()
        self.assertEqual(len(self._search_purchases()), 1)
