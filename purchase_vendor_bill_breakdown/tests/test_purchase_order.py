from odoo import exceptions, fields
from odoo.tests import Form, tagged

from .common import PurchaseTransactionCase


@tagged("post_install", "-at_install", "test_purchase_order")
class TestPurchaseOrder(PurchaseTransactionCase):
    """
    TEST 1 - Changed state 'Use Product Component' when partner changed
    TEST 2 - Check invoice line struct by 'use_product_components' state
    TEST 3 - Creating an invoice with state 'to invoice'
    TEST 4 - Creating an invoice with state 'refund'
    TEST 5 - Activate components after purchase order creation
    TEST 6 - Disable components activation after product receiving
    """

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()

        with Form(self.purchase_order_test_1) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 500.0
            line.product_qty = 5.0

    # TEST 1 - Changed state 'Use Product Component' when partner changed
    def test_purchase_order_set_use_product_component(self):
        """Changed state 'Use Product Component' when partner changed"""
        with Form(self.env["purchase.order"]) as form:
            self.assertFalse(
                form.use_product_components, msg="'Use Product Component' must be False"
            )
            form.partner_id = self.res_partner_test
            self.assertFalse(
                form.use_product_components, msg="'Use Product Component' must be False"
            )
            form.partner_id = self.res_partner_test_use_product_components
            self.assertTrue(
                form.use_product_components, msg="'Use Product Component' must be True"
            )

    # TEST 2 - Check invoice line struct by 'use_product_components' state
    def test_prepare_invoice(self):
        """Check invoice line struct by 'use_product_components' state"""
        order = self.purchase_order_test_1
        order.write({"use_product_components": False})
        invoice_vals = order._prepare_invoice()
        self.assertFalse(
            invoice_vals["invoice_line_ids"],
            msg="Invoice line ids must be empty list",
        )
        order.write({"use_product_components": True})
        order.button_confirm()
        order.order_line.write({"qty_received": 1})
        invoice_vals = order._prepare_invoice()
        self.assertEqual(
            len(invoice_vals["invoice_line_ids"]),
            2,
            msg="Count invoice line must be equal to 2",
        )

    # TEST 3 - Creating an invoice with state 'to invoice'
    def test_get_invoiced(self):
        """Creating an invoice with state 'to invoice'"""
        order = self.purchase_order_test_1
        order.button_confirm()
        self.assertEqual(
            order.invoice_status, "no", msg="Invoice status must be equal to 'no'"
        )
        order.order_line[0].qty_received = 1
        self.assertEqual(
            order.invoice_status,
            "to invoice",
            msg="Invoice status must be equal to 'to invoice'",
        )
        order.action_create_invoice()
        order._get_invoiced()
        self.assertEqual(
            order.invoice_status,
            "invoiced",
            msg="Invoice status must be equal to 'invoiced'",
        )

    # TEST 4 - Creating an invoice with state 'refund'
    def test_refund_components(self):
        """Creating an invoice with state 'refund'"""
        order = self.purchase_order_test_1
        order.button_confirm()
        order.order_line.write({"qty_received": 2})
        component_1, component_2 = order.order_line.component_ids
        self.assertEqual(
            int(component_1.total_qty),
            10,
            msg="Total Qty for component #1 must be equal to 10",
        )
        self.assertEqual(
            int(component_2.total_qty),
            6,
            msg="Total Qty for component #2 must be equal to 6",
        )
        order.action_create_invoice()
        self.assertEqual(
            int(component_1.qty_invoiced),
            10,
            msg="Total Qty for component #1 must be equal to 10",
        )
        self.assertEqual(
            int(component_2.qty_invoiced),
            6,
            msg="Total Qty for component #2 must be equal to 6",
        )
        move_ids = order.invoice_ids
        self.assertEqual(
            len(move_ids), 1, msg="Account move records must be equal to 1"
        )
        with Form(move_ids) as form:
            form.invoice_date = fields.Date.today()
        move_ids.action_post()
        move_reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=move_ids.ids)
            .create(
                {
                    "date": fields.Date.today(),
                    "reason": "no reason",
                    "refund_method": "refund",
                }
            )
        )
        move_reversal.reverse_moves()
        self.assertEqual(
            int(component_1.qty_invoiced),
            0,
            msg="Total Qty for component #1 must be equal to 0",
        )
        self.assertEqual(
            int(component_2.qty_invoiced),
            0,
            msg="Total Qty for component #2 must be equal to 0",
        )

    # TEST 5 - Activate components after purchase order creation
    def test_activate_components_after_order_creation(self):
        """Activate components after purchase order creation"""
        line = self.purchase_order_without_components.order_line
        self.assertFalse(line.component_ids, msg="Components recordset must be empty")

        with Form(self.purchase_order_without_components) as form:
            form.use_product_components = True
        self.assertEqual(
            len(line.component_ids),
            2,
            msg="Count components must be equal to 2",
        )

    # TEST 6 - Disable components activation after product receiving
    def test_disable_components_activation_after_product_receiving(self):
        """Disable components activation after product receiving"""
        self.purchase_order_without_components.button_confirm()
        self.purchase_order_without_components.order_line.write({"qty_received": 1})
        self.purchase_order_without_components.action_create_invoice()
        with self.assertRaises(exceptions.UserError):
            with Form(self.purchase_order_without_components) as form:
                form.use_product_components = True
