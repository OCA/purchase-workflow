from odoo.tests import Form, tagged

from odoo.addons.purchase_vendor_bill_breakdown.tests.common import (
    PurchaseTransactionCase,
)


@tagged("post_install", "-at_install", "test_stock_purchase_order_line")
class TestStockPurchaseOrderLine(PurchaseTransactionCase):
    def test_stock_purchase_order_line_with_bill_components(self):
        StockBackorderConfirmation = self.env["stock.backorder.confirmation"]
        order = self.purchase_order_test_1
        with Form(order) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 10
        order.button_confirm()
        self.assertTrue(
            order.use_product_components,
            msg="Purchase Order Vendor Bill Breakdown must be True",
        )
        self.assertEqual(
            order.order_line.qty_received,
            0,
            msg="Received Qty must be equal to 0",
        )

        components = order.order_line.mapped("component_ids")
        self.assertEqual(len(components), 2, msg="Components count must be equal to 2")
        component_1, component_2 = order.order_line.mapped("component_ids")
        self.assertEqual(component_1.total_qty, 0, msg="Total Qty must be equal to 0")
        self.assertEqual(component_2.total_qty, 0, msg="Total Qty must be equal to 0")

        picking = order.picking_ids.sorted("id")
        # Progress 6.0 out of the 10.0 ordered qty
        picking.move_lines.quantity_done = 6
        result_dict = picking.button_validate()
        # Create backorder
        StockBackorderConfirmation.with_context(**result_dict["context"]).process()

        self.assertEqual(
            order.order_line.qty_received,
            6,
            msg="Received Qty must be equal to 6",
        )
        self.env.add_to_compute(
            order.order_line._fields["qty_received"], order.order_line
        )
        order.order_line.recompute()
        order.order_line.flush()
        component_1, component_2 = order.order_line.mapped("component_ids")
        # Get Product Components
        self.assertEqual(
            component_1.total_qty, 30.0, msg="Total Qty must be equal to 30.0"
        )
        self.assertEqual(
            component_2.total_qty, 18.0, msg="Total Qty must be equal to 18.0"
        )
        order.action_create_invoice()
        self.assertEqual(
            len(order.invoice_ids),
            1,
            msg="Invoice Count must be equal to 1",
        )
        line = order.order_line
        self.assertEqual(line.qty_invoiced, 6, msg="Qty Invoiced must be equal to 6")
        inv_component_1, inv_component_2 = line.invoice_lines
        self.assertEqual(
            round(inv_component_1.quantity, 2), 30, msg="Qty must be equal to 30"
        )
        self.assertEqual(
            round(inv_component_2.quantity, 2), 18, msg="Qty must be equal to 18"
        )

        *_, picking = order.picking_ids.sorted("id")
        # Progress 4.0 out of the 4.0 ordered qty
        picking.move_lines.quantity_done = 4.0
        result_dict = picking.button_validate()
        self.assertTrue(result_dict, msg="Result must be True")

        self.assertEqual(
            order.order_line.qty_received,
            10,
            msg="Received Qty must be equal to 10",
        )
        self.env.add_to_compute(
            order.order_line._fields["qty_received"], order.order_line
        )
        order.order_line.recompute()
        order.order_line.flush()
        # order.order_line._compute_qty_received()
        component_1, component_2 = order.order_line.mapped("component_ids")
        self.assertEqual(
            component_1.total_qty, 50.0, msg="Total Qty must be equal to 50.0"
        )
        self.assertEqual(
            component_2.total_qty, 30.0, msg="Total Qty must be equal to 30.0"
        )
        order.action_create_invoice()

        self.assertEqual(
            len(order.invoice_ids),
            2,
            msg="Invoice Count must be equal to 2",
        )
        line = order.order_line
        self.assertEqual(line.qty_invoiced, 10, msg="Qty Invoiced must be equal to 10")
        (
            *_,
            invoice_line_component_1,
            invoice_line_component_2,
        ) = line.invoice_lines.sorted("id")
        self.assertEqual(
            round(invoice_line_component_1.quantity, 2),
            20,
            msg="Qty must be equal to 20",
        )
        self.assertEqual(
            round(invoice_line_component_2.quantity, 2),
            12,
            msg="Qty must be equal to 12",
        )

    def test_stock_purchase_order_line_without_bill_components(self):
        order = self.purchase_order_test_2
        with Form(order) as form, form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 10
        order.button_confirm()
        self.assertEqual(
            order.order_line.qty_received,
            0,
            msg="Received Qty must be equal to 0",
        )

        components = order.order_line.mapped("component_ids")
        self.assertEqual(len(components), 0, msg="Components count must be equal to 0")
        picking = order.picking_ids
        # Progress 10.0 out of the 10.0 ordered qty
        picking.move_lines.quantity_done = 10.0
        result_dict = picking.button_validate()
        order.action_create_invoice()
        self.assertTrue(result_dict, msg="Result must be True")
        self.assertEqual(
            order.order_line.qty_received,
            10,
            msg="Received Qty must be equal to 0",
        )
        invoice_line_product = order.order_line.invoice_lines.sorted("id")
        self.assertEqual(
            len(invoice_line_product), 1, msg="Invoice Qty must be equal to 1"
        )
        self.assertEqual(
            round(invoice_line_product.quantity, 2), 10, msg="Qty must be equal to 10"
        )
