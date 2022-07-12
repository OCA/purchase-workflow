# Copyright 2015-2017 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestProcurementPurchaseNoGrouping(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestProcurementPurchaseNoGrouping, cls).setUpClass()
        cls.category = cls.env["product.category"].create({"name": "Test category"})
        cls.customer = cls.env["res.partner"].create({"name": "Test customer"})
        cls.supplier = cls.env["res.partner"].create({"name": "Test supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product service",
                "type": "service",
                "categ_id": cls.category.id,
                "service_to_purchase": True,
                "seller_ids": [(0, 0, {"name": cls.supplier.id, "min_qty": 1.0})],
            }
        )
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.customer.id})
        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 2,
                "product_uom": cls.product.uom_id.id,
                "price_unit": 10,
            }
        )

    def test_procurement_no_grouping_order_purchase_service(self):
        self.category.procured_purchase_grouping = "order"
        self.sale_order.action_confirm()
        orders = self.env["purchase.order"].search(
            [("origin", "=", self.sale_order.name)]
        )
        self.assertEqual(
            len(orders),
            1,
            "Procured purchase orders are the same",
        )
        self.assertEqual(
            len(orders.mapped("order_line")),
            1,
            "Procured purchase orders lines are the same",
        )
        sale_order_2 = self.sale_order.copy()
        # Duplicate line to have 2 distinct lines with the same product
        sale_order_2.order_line.copy({"order_id": sale_order_2.id})
        sale_order_2.action_confirm()
        orders = self.env["purchase.order"].search([("origin", "=", sale_order_2.name)])
        self.assertEqual(
            len(orders),
            2,
            "Procured purchase orders are the same",
        )
        self.assertEqual(
            len(orders.mapped("order_line")),
            2,
            "Procured purchase orders lines are the same",
        )
