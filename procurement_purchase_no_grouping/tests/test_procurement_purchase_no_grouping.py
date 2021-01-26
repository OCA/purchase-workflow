# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestProcurementPurchaseNoGrouping(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProcurementPurchaseNoGrouping, cls).setUpClass()
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product_1 = cls._create_product(
            cls, 'Test product 1', cls.category, cls.partner
        )
        cls.product_2 = cls._create_product(
            cls, 'Test product 2', cls.category, cls.partner
        )
        cls.location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type = cls.env.ref('stock.picking_type_in')
        cls.origin = "Manual Replenishment"
        cls.prev_orders = cls.env['purchase.order'].search([
            ("origin", "=", cls.origin),
        ])
        cls.stock_location_route = cls.env.ref(
            'purchase_stock.route_warehouse0_buy')
        cls.stock_rule = cls.stock_location_route.rule_ids[0]

    def _create_product(self, name, category, partner):
        product = self.env['product.product'].create({
            'name': name,
            'categ_id': category.id,
            'seller_ids': [
                (0, 0, {
                    'name': partner.id,
                    'min_qty': 1.0,
                }),
            ]}
        )
        return product

    def _run_procurement(self, product):
        wizard = self.env["product.replenish"].with_context(
            default_product_id=product.id
        ).create({})
        wizard.launch_replenishment()

    def _search_purchases(self):
        return self.env['purchase.order'].search([
            ("origin", "=", self.origin),
            ("id", "not in", self.prev_orders.ids),
        ])

    def test_procurement_grouped_purchase(self):
        self.category.procured_purchase_grouping = 'standard'
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_2)
        orders = self._search_purchases()
        self.assertEqual(
            len(orders), 1, 'Procured purchase orders are not the same',
        )
        self.assertEqual(
            len(orders.order_line), 2,
            'Procured purchase orders lines are not the same',
        )

    def test_procurement_no_grouping_line_purchase(self):
        self.category.procured_purchase_grouping = 'line'
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_2)
        orders = self._search_purchases()
        self.assertEqual(
            len(orders), 1, 'Procured purchase orders are not the same',
        )
        self.assertEqual(
            len(orders.order_line), 3,
            'Procured purchase orders lines are the same',
        )

    def test_procurement_no_grouping_order_purchase(self):
        self.category.procured_purchase_grouping = 'order'
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_2)
        orders = self._search_purchases()
        self.assertEqual(
            len(orders), 3, 'Procured purchase orders are the same',
        )
        self.assertEqual(
            len(orders.mapped('order_line')), 3,
            'Procured purchase orders lines are the same',
        )

    def test_procurement_products_same_category(self):
        self.category.procured_purchase_grouping = 'product_category'
        self._run_procurement(self.product_1)
        self._run_procurement(self.product_2)
        self._run_procurement(self.product_1)
        orders = self._search_purchases()
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(orders.mapped('order_line')), 2)

    def test_procurement_products_distinct_category(self):
        self.category.procured_purchase_grouping = 'product_category'
        category2 = self.category.copy()
        self._run_procurement(self.product_1)
        self.product_2.categ_id = category2.id
        self._run_procurement(self.product_2)
        self._run_procurement(self.product_1)
        orders = self._search_purchases()
        self.assertEqual(len(orders), 2)
