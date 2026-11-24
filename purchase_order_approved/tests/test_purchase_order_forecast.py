# Copyright 2026 Versada UAB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseOrderForecast(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.company.purchase_approve_active = True
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "route_ids": [Command.set(cls.warehouse.buy_pull_id.route_id.ids)],
                "seller_ids": [Command.create({"partner_id": cls.vendor.id})],
            }
        )

    def _create_approved_order(self, quantity):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product.id, "product_qty": quantity}
                    )
                ],
            }
        )
        order.button_confirm()
        return order.filtered(lambda order: order.state == "approved").ensure_one()

    def test_orderpoint_counts_approved_order(self):
        self._create_approved_order(10.0)
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 5.0,
                "product_max_qty": 10.0,
            }
        )
        self.assertEqual(orderpoint.qty_forecast, 10.0)
        self.assertEqual(orderpoint.qty_to_order, 0.0)

    def test_forecasted_report_counts_approved_order(self):
        order = self._create_approved_order(10.0)
        header = self.env["stock.forecasted_product_product"].get_report_values(
            docids=self.product.ids
        )["docs"]
        self.assertEqual(header["draft_purchase_qty"], 10.0)
        self.assertEqual(header["qty"]["in"], 10.0)
        self.assertEqual(
            header["draft_purchase_orders"], [{"id": order.id, "name": order.name}]
        )
