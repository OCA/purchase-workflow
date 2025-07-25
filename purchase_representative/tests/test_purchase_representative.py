from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseRepresentative(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_test = self.env["res.users"].create(
            {
                "email": "testuser@testuser.com",
                "name": "Test User",
                "login": "test_user",
                "password": "test_user",
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Partner Test",
                "supplier_rank": 1,
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Product Test",
                "is_storable": True,
                "route_ids": [
                    (6, 0, [self.env.ref("purchase_stock.route_warehouse0_buy").id])
                ],
                "standard_price": 50.0,
            }
        )

        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "min_qty": 1.0,
                "price": 45.0,
            }
        )

        self.location = self.env.ref("stock.stock_location_stock")
        self.picking_type = self.env.ref("stock.picking_type_in")

    def test_create_procurement(self):
        """Test that the user_id field is filled automatically"""
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            10,
            self.product.uom_id,
            self.location,
            name="Procurement Test",
            origin="Test Origin",
            company_id=self.env.company,
            values={
                "company_id": self.env.company,
                "date_planned": fields.Datetime.now(),
                "warehouse_id": self.env.ref("stock.warehouse0").id,
                "procure_method": "make_to_order",
            },
        )
        self.env["stock.rule"].with_user(self.user_test)._run_buy(
            [(procurement, self.env["stock.rule"].search([], limit=1))]
        )

        purchase_orders = self.env["purchase.order"].search(
            [("origin", "=", "Test Origin")]
        )
        self.assertEqual(len(purchase_orders), 1)
        po = purchase_orders[0]
        self.assertEqual(po.partner_id, self.partner)
        self.assertEqual(len(po.order_line), 1)
        self.assertEqual(po.order_line[0].product_id, self.product)

        self.assertEqual(po.user_id.id, self.user_test.id)
