# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestStockRule(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockRule, cls).setUpClass()
        cls.supplierinfo_obj = cls.env["product.supplierinfo"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Mrs. Odoo 2",
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Test Product 1",
                "purchase_method": "purchase",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "purchase_method": "purchase",
            }
        )
        cls.supplierinfo = cls.supplierinfo_obj.create(
            {
                "partner_id": cls.partner2.id,
                "purchase_partner_id": cls.partner.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "price": 100,
            }
        )
        cls.supplierinfo2 = cls.supplierinfo_obj.create(
            {
                "partner_id": cls.partner2.id,
                "product_tmpl_id": cls.product2.product_tmpl_id.id,
                "price": 50,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location_id = cls.warehouse.lot_stock_id.id

    def test_replenishment_with_vendor_purchase(self):
        op = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": self.product1.name,
                "location_id": self.stock_location_id,
                "product_id": self.product1.id,
                "product_min_qty": 1,
                "product_max_qty": 8,
                "trigger": "manual",
            }
        )
        op.action_replenish()
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.partner.id)], order="id desc", limit=1
        )
        self.assertEqual(purchase.partner_id, self.supplierinfo.purchase_partner_id)
        self.assertEqual(purchase.order_line.product_id, self.product1)
        self.assertEqual(purchase.order_line.price_unit, self.supplierinfo.price)
        self.assertEqual(purchase.order_line.product_qty, 8)
        self.assertEqual(purchase.currency_id, self.supplierinfo.currency_id)

    def test_replenishment_without_vendor_purchase(self):
        op = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": self.product2.name,
                "location_id": self.stock_location_id,
                "product_id": self.product2.id,
                "product_min_qty": 1,
                "product_max_qty": 10,
                "trigger": "manual",
            }
        )
        op.action_replenish()
        purchase = self.env["purchase.order"].search(
            [("partner_id", "=", self.partner2.id)], order="id desc", limit=1
        )
        self.assertEqual(purchase.partner_id, self.supplierinfo2.partner_id)
        self.assertEqual(purchase.order_line.product_id, self.product2)
        self.assertEqual(purchase.order_line.price_unit, self.supplierinfo2.price)
        self.assertEqual(purchase.order_line.product_qty, 10)
        self.assertEqual(purchase.currency_id, self.supplierinfo2.currency_id)
