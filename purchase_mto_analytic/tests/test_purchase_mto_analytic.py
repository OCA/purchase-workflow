# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseMtoAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        purchase_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        # Get the MTO route and activate it if necessary
        mto_route = cls.env.ref("stock.route_warehouse0_mto")
        if not mto_route.active:
            mto_route.write({"active": True})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "product",
                "route_ids": [(6, 0, [mto_route.id, purchase_route.id])],
            }
        )
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor 1"})
        cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.vendor.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "test plan", "company_id": False}
        )
        analytic_account = cls.env["account.analytic.account"].create(
            {"name": "test account", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution = {str(analytic_account.id): 100}

    def test_purchase_analytic(self):
        # Create an outgoing stock picking for the product
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        picking_type_out = self.env.ref("stock.picking_type_out")
        stock_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test: move out",
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "procure_method": "make_to_order",
                            "product_uom": self.product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                            "analytic_distribution": self.analytic_distribution,
                        },
                    ),
                ],
            }
        )
        # Confirm the stock picking
        stock_picking.action_confirm()
        purchase_order = self.env["purchase.order"].search(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertTrue(purchase_order, "No purchase order created.")
        self.assertEqual(
            purchase_order.analytic_distribution, self.analytic_distribution
        )
