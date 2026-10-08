from odoo import Command, fields
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRepresentative(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_test = new_test_user(
            cls.env,
            login="test_user",
            groups="purchase.group_purchase_user",
            name="Test User",
            email="testuser@testuser.com",
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "is_storable": True,
                "route_ids": [
                    Command.set([cls.env.ref("purchase_stock.route_warehouse0_buy").id])
                ],
                "standard_price": 50.0,
            }
        )

        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "min_qty": 1.0,
                "price": 45.0,
            }
        )

        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type = cls.env.ref("stock.picking_type_in")

    def test_create_procurement(self):
        """Test that the user_id field is filled automatically"""
        procurement = self.env["stock.rule"].Procurement(
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
        rule = self.env["stock.rule"].search([("action", "=", "buy")], limit=1)
        if not rule:
            rule = self.env["stock.rule"].search([], limit=1)
        self.env["stock.rule"].with_user(self.user_test)._run_buy([(procurement, rule)])

        purchase_orders = self.env["purchase.order"].search(
            [("origin", "=", "Test Origin")]
        )
        self.assertEqual(len(purchase_orders), 1)
        po = purchase_orders[0]
        self.assertEqual(po.partner_id, self.partner)
        self.assertEqual(len(po.order_line), 1)
        self.assertEqual(po.order_line[0].product_id, self.product)

        self.assertEqual(po.user_id.id, self.user_test.id)
