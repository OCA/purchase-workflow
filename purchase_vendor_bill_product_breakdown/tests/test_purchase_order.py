from odoo.fields import Date
from odoo.tests import tagged

from .common import PurchaseTransactionCase


@tagged("post_install", "-at_install")
class TestPurchaseOrder(PurchaseTransactionCase):
    def test_purchase_order_set_bill_components(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "name": self.product_product_test_1.name,
                            "price_unit": 79.80,
                            "product_qty": 15.0,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(
            order.bill_components, msg="Order Bill Components must be False"
        )
        self.res_partner_test.write({"bill_components": True})
        self.assertFalse(
            order.bill_components, msg="Order Bill Components must be False"
        )
        order.write({"partner_id": self.res_partner_test_bill_components.id})
        order.set_partner_bill_components()
        self.assertTrue(order.bill_components, msg="Order Bill Components must be True")
        self.res_partner_test_bill_components.write({"bill_components": False})
        self.assertTrue(order.bill_components, msg="Order Bill Components must be True")

    def test_prepare_invoice(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test_bill_components.id,
                "bill_components": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "name": self.product_product_test_1.name,
                            "price_unit": 500.0,
                            "product_qty": 5.0,
                        },
                    ),
                ],
            }
        )
        order.write({"bill_components": False})
        invoice_vals = order._prepare_invoice()
        self.assertEqual(
            invoice_vals["invoice_line_ids"],
            [],
            msg="Invoice line ids must be empty list",
        )
        order.write({"bill_components": True})
        order.button_confirm()
        order.order_line.write({"qty_received": 1})
        invoice_vals = order._prepare_invoice()
        self.assertEqual(
            len(invoice_vals["invoice_line_ids"]),
            2,
            msg="Count invoice line must be equal 2",
        )

    def test_get_invoiced(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test_bill_components.id,
                "bill_components": True,
            }
        )
        order_line = (
            self.env["purchase.order.line"].create(
                {
                    "order_id": order.id,
                    "product_id": self.product_product_test_1.id,
                    "name": self.product_product_test_1.name,
                    "price_unit": 500.0,
                    "product_qty": 5.0,
                }
            ),
        )
        order.button_confirm()
        self.assertEqual(
            order.invoice_status, "no", msg="Invoice status must be equal 'no'"
        )
        order_line[0].qty_received = 1
        self.assertEqual(
            order.invoice_status,
            "to invoice",
            msg="Invoice status must be equal 'to invoice'",
        )
        order.action_create_invoice()
        order._get_invoiced()
        self.assertEqual(
            order.invoice_status,
            "invoiced",
            msg="Invoice status must be equal 'invoiced'",
        )

    def test_refund_components(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner_test_bill_components.id,
                "bill_components": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product_test_1.id,
                            "name": self.product_product_test_1.name,
                            "price_unit": 500.0,
                            "product_qty": 5.0,
                        },
                    )
                ],
            }
        )
        order_line = order.order_line[0]
        order.button_confirm()
        order_line.qty_received = 2
        component_1 = order_line.component_ids[0]
        component_2 = order_line.component_ids[1]
        self.assertEqual(
            int(component_1.total_qty),
            10,
            msg="Total Qty for component #1 must be equal 10",
        )
        self.assertEqual(
            int(component_2.total_qty),
            6,
            msg="Total Qty for component #2 must be equal 6",
        )
        order.action_create_invoice()
        self.assertEqual(
            int(component_1.qty_invoiced),
            10,
            msg="Total Qty for component #1 must be equal 10",
        )
        self.assertEqual(
            int(component_2.qty_invoiced),
            6,
            msg="Total Qty for component #2 must be equal 6",
        )
        move_ids = order.invoice_ids
        self.assertEqual(len(move_ids), 1, msg="Account move records must be equal 1")
        move_ids.invoice_date = Date.today()
        move_ids.action_post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=move_ids.ids)
            .create(
                {
                    "date": Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                }
            )
        )
        move_reversal.reverse_moves()
        self.assertEqual(
            int(component_1.qty_invoiced),
            0,
            msg="Total Qty for component #1 must be equal 0",
        )
        self.assertEqual(
            int(component_2.qty_invoiced),
            0,
            msg="Total Qty for component #2 must be equal 0",
        )
