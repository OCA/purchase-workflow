from odoo.exceptions import UserError
from odoo.tests import Form, common

from .common import PurchaseTransactionCase


@common.tagged("post_install", "-at_install", "test_components_flow")
class TestComponentsFlow(PurchaseTransactionCase):
    """
    TEST 1 - Check correct module flow
    TEST 2 - Check default flow is not broken
    """

    def setUp(self):
        super(TestComponentsFlow, self).setUp()
        PurchaseOrder = self.env["purchase.order"]
        with Form(self.product_product_test_1) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 1.0

        with Form(
            self.product_product_test_1.seller_ids[0], view=self.view_name
        ) as form:
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_1
                line.product_uom_qty = 1.0
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_2
                line.product_uom_qty = 2.0
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_3
                line.product_uom_qty = 3.0

        with Form(self.product_product_component_test_1) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 100.0
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 200.0

        with Form(self.product_product_component_test_2) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 150.0

        with Form(self.product_product_component_test_3) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 200.0

        with Form(self.product_product_component_test_4) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 180.0

        with Form(self.product_product_component_test_5) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 170.0

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test_use_product_components
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 5
            line.price_unit = 10.0
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_2
            line.product_qty = 5
            line.price_unit = 20.0
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_3
            line.product_qty = 5
            line.price_unit = 30.0
        self.purchase_order_1_test = form.save()
        self.purchase_order_1_test.button_confirm()

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 5
            line.price_unit = 10.0
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_2
            line.product_qty = 5
            line.price_unit = 20.0
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_3
            line.product_qty = 5
            line.price_unit = 30.0
        self.purchase_order_2_test = form.save()
        self.purchase_order_2_test.button_confirm()

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test_use_product_components
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 4.0
            line.product_qty = 4.0
        self.purchase_order_2_test_1 = form.save()

    # TEST 1 - Check correct module flow
    def test_request_for_quotation_flow_with_components(self):
        """Check correct module flow"""
        purchase_order = self.purchase_order_1_test
        self.assertTrue(
            purchase_order.use_product_components,
            msg="Purchase Order Vendor Bill Breakdown must be equal True",
        )

        (
            purchase_order_line_1,
            purchase_order_line_2,
            purchase_order_line_3,
        ) = purchase_order.order_line.sorted("id")
        self.assertEqual(
            len(purchase_order_line_1.component_ids),
            2,
            msg="Count components must be equal to 2",
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal to 0",
        )

        self.assertEqual(
            len(purchase_order_line_2.component_ids),
            0,
            msg="Count components must be equal to 0",
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal to 0",
        )

        self.assertEqual(
            len(purchase_order_line_3.component_ids),
            0,
            msg="Count components must be equal to 0",
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal to 0",
        )

        uom_id = self.ref("uom.product_uom_unit")

        self.env["purchase.order.line.component"].create(
            {
                "line_id": purchase_order_line_2.id,
                "component_id": self.product_product_component_test_4.id,
                "product_uom_qty": 3,
                "product_uom_id": uom_id,
            }
        )
        self.env["purchase.order.line.component"].create(
            {
                "line_id": purchase_order_line_2.id,
                "component_id": self.product_product_component_test_5.id,
                "product_uom_qty": 2,
                "product_uom_id": uom_id,
            }
        )

        self.assertEqual(
            len(purchase_order_line_2.component_ids),
            2,
            msg="Count components must be equal to 2",
        )
        with self.assertRaises(
            UserError, msg="Action must be raised UserError exception"
        ):
            purchase_order.action_create_invoice()

        purchase_order.order_line.write({"qty_received": 3})

        (
            pol_1_component_1,
            pol_1_component_2,
        ) = purchase_order_line_1.component_ids.sorted("id")
        self.assertEqual(
            pol_1_component_1.total_qty,
            15,
            msg="Component total Qty must be equal to 15",
        )
        self.assertEqual(
            pol_1_component_2.total_qty, 9, msg="Component total Qty must be equal to 6"
        )

        (
            pol_2_component_1,
            pol_2_component_2,
        ) = purchase_order_line_2.component_ids.sorted("id")
        self.assertEqual(
            pol_2_component_1.total_qty, 9, msg="Component total Qty must be equal to 9"
        )
        self.assertEqual(
            pol_2_component_2.total_qty, 6, msg="Component total Qty must be equal to 6"
        )

        pol_1_component_1.total_qty += 1.52

        self.assertEqual(
            pol_1_component_1.total_qty,
            16.52,
            msg="Component total Qty must be equal to 16.52",
        )
        purchase_order.action_create_invoice()

        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            3,
            msg="Last Invoiced Qty must be equal to 3",
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            3,
            msg="Last Invoiced Qty must be equal to 3",
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal to 0",
        )
        self.assertEqual(
            len(purchase_order_line_1.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal to 2",
        )
        self.assertEqual(
            len(purchase_order_line_2.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal to 2",
        )
        self.assertEqual(
            len(purchase_order_line_3.invoice_lines),
            1,
            msg="Count elements in invoice by order line must be equal to 1",
        )
        self.assertEqual(
            len(purchase_order.invoice_ids), 1, msg="Count Invoice must be equal to 1"
        )

        invoice_1_line_1, invoice_1_line_2 = purchase_order_line_1.invoice_lines.sorted(
            "id"
        )
        self.assertEqual(
            round(invoice_1_line_1.quantity, 2), 16.52, msg="Qty must be equal to 16.52"
        )
        self.assertEqual(
            invoice_1_line_1.price_unit, 100.0, msg="Unit Price must be equal to 100.0"
        )
        self.assertEqual(
            round(invoice_1_line_1.price_subtotal, 2),
            1652.0,
            msg="Subtotal must be equal to 1652.0",
        )

        self.assertEqual(invoice_1_line_2.quantity, 9, msg="Qty must be equal to 9")
        self.assertEqual(
            invoice_1_line_2.price_unit, 150.0, msg="Unit price must be equal to 150.0"
        )
        self.assertEqual(
            invoice_1_line_2.price_subtotal,
            1350.0,
            msg="Subtotal must be equal to 1350.0",
        )

        invoice_2_line_1, invoice_2_line_2 = purchase_order_line_2.invoice_lines.sorted(
            "id"
        )
        self.assertEqual(invoice_2_line_1.quantity, 9, msg="Qty must be equal to 9")
        self.assertEqual(
            invoice_2_line_1.price_unit, 180.0, msg="Unit price must be equal to 180.0"
        )
        self.assertEqual(
            invoice_2_line_1.price_subtotal,
            1620.0,
            msg="Subtotal must be equal to 1620.0",
        )

        self.assertEqual(invoice_2_line_2.quantity, 6, msg="Qty must be equal to 6")
        self.assertEqual(
            invoice_2_line_2.price_unit, 170.0, msg="Unit price must be equal to 170.0"
        )
        self.assertEqual(
            invoice_2_line_2.price_subtotal,
            1020.0,
            msg="Subtotal must be equal to 1020.0",
        )

        invoice_3_line_1 = purchase_order_line_3.invoice_lines.sorted("id")
        self.assertEqual(invoice_3_line_1.quantity, 3, msg="Qty must be equal to 3")
        self.assertEqual(
            invoice_3_line_1.price_unit, 30, msg="Unit price must be equal to 30"
        )
        self.assertEqual(
            invoice_3_line_1.price_subtotal, 90, msg="Subtotal must be equal to 90"
        )

        self.assertEqual(
            purchase_order_line_1.qty_received, 3, msg="Received Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_2.qty_received, 3, msg="Received Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_3.qty_received, 3, msg="Received Qty must be equal to 3"
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 3, msg="Invoiced Qty must be equal to 3"
        )
        self.assertEqual(
            round(pol_1_component_1.qty_invoiced, 2),
            16.52,
            msg="Invoiced Qty must be equal to 16.52",
        )
        self.assertEqual(
            pol_1_component_2.qty_invoiced, 9, msg="Invoiced Qty must be equal to 9"
        )
        self.assertEqual(
            pol_2_component_1.qty_invoiced, 9, msg="Invoiced Qty must be equal to 9"
        )
        self.assertEqual(
            pol_2_component_2.qty_invoiced, 6, msg="Invoiced Qty must be equal to 6"
        )

        purchase_order.order_line.write({"qty_received": 5})
        self.assertEqual(
            round(pol_1_component_1.total_qty, 2),
            26.52,
            msg="Component total Qty must be equal  to 26.52",
        )
        self.assertEqual(
            pol_1_component_2.total_qty,
            15,
            msg="Component total Qty must be equal to 15",
        )
        self.assertEqual(
            pol_2_component_1.total_qty,
            15,
            msg="Component total Qty must be equal to 15",
        )
        self.assertEqual(
            pol_2_component_2.total_qty,
            10,
            msg="Component total Qty must be equal to 10",
        )

        purchase_order.action_create_invoice()

        self.assertEqual(
            len(purchase_order.invoice_ids), 2, msg="Count Invoice must be equal to 2"
        )
        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            5,
            msg="Last Invoiced Qty must be equal 5",
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            5,
            msg="Last Invoiced Qty must be equal 5",
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            len(purchase_order_line_1.invoice_lines),
            4,
            msg="Count elements in invoice by order line must be equal 4",
        )
        self.assertEqual(
            len(purchase_order_line_2.invoice_lines),
            4,
            msg="Count elements in invoice by order line must be equal 4",
        )
        self.assertEqual(
            len(purchase_order_line_3.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal 2",
        )
        (
            *_,
            invoice_1_line_1,
            invoice_1_line_2,
        ) = purchase_order_line_1.invoice_lines.sorted("id")

        self.assertEqual(
            round(invoice_1_line_1.quantity, 2), 10, msg="Qty must be equal 10"
        )
        self.assertEqual(
            round(invoice_1_line_1.price_subtotal, 2),
            1000.0,
            msg="Subtotal must be equal 1000.0",
        )

        self.assertEqual(invoice_1_line_2.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_1_line_2.price_subtotal, 900.0, msg="Subtotal must be equal 900.0"
        )

        (
            *_,
            invoice_2_line_1,
            invoice_2_line_2,
        ) = purchase_order_line_2.invoice_lines.sorted("id")
        self.assertEqual(invoice_2_line_1.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_2_line_1.price_subtotal, 1080.0, msg="Subtotal must be equal 1080.0"
        )

        self.assertEqual(invoice_2_line_2.quantity, 4, msg="Qty must be equal 4")
        self.assertEqual(
            invoice_2_line_2.price_subtotal, 680.0, msg="Subtotal must be equal 680.0"
        )

        *_, invoice_3_line_1 = purchase_order_line_3.invoice_lines
        self.assertEqual(invoice_3_line_1.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_3_line_1.price_subtotal, 60, msg="Subtotal must be equal 60"
        )
        self.assertEqual(
            round(pol_1_component_1.total_qty, 2),
            26.52,
            msg="Component total Qty must be equal 26.52",
        )
        self.assertEqual(
            pol_1_component_2.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_1.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_2.total_qty, 10, msg="Component total Qty must be equal 10"
        )

    # TEST 2 - Check default flow is not broken
    def test_request_for_quotation_flow_without_components(self):
        """Check default flow is not broken"""
        purchase_order = self.purchase_order_2_test
        self.assertFalse(
            purchase_order.use_product_components,
            msg="Purchase Order Vendor Bill Breakdown must be equal True",
        )

        (
            purchase_order_line_1,
            purchase_order_line_2,
            purchase_order_line_3,
        ) = purchase_order.order_line.sorted("id")
        self.assertEqual(
            len(purchase_order_line_1.component_ids),
            0,
            msg="Count components must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal 0",
        )

        self.assertEqual(
            len(purchase_order_line_2.component_ids),
            0,
            msg="Count components must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal 0",
        )

        self.assertEqual(
            len(purchase_order_line_3.component_ids),
            0,
            msg="Count components must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal 0",
        )

        purchase_order.order_line.write({"qty_received": 3})

        purchase_order.action_create_invoice()

        invoice_line_1 = purchase_order_line_1.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_1.quantity, 3, msg="Qty must be equal 2")
        self.assertEqual(
            round(invoice_line_1.price_subtotal, 2), 30, msg="Subtotal must be equal 30"
        )
        invoice_line_2 = purchase_order_line_2.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_2.quantity, 3, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_line_2.price_subtotal, 60, msg="Subtotal must be equal 60"
        )
        invoice_line_3 = purchase_order_line_3.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_3.quantity, 3, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_line_3.price_subtotal, 90, msg="Subtotal must be equal 90"
        )

        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            len(purchase_order_line_1.invoice_lines),
            1,
            msg="Count elements in invoice by order line must be equal 1",
        )
        self.assertEqual(
            len(purchase_order_line_2.invoice_lines),
            1,
            msg="Count elements in invoice by order line must be equal 1",
        )
        self.assertEqual(
            len(purchase_order_line_3.invoice_lines),
            1,
            msg="Count elements in invoice by order line must be equal 1",
        )
        self.assertEqual(
            len(purchase_order.invoice_ids), 1, msg="Count Invoice must be equal 1"
        )

        purchase_order.order_line.write({"qty_received": 5})

        purchase_order.action_create_invoice()

        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 5, msg="Invoiced Qty must be equal 5"
        )
        self.assertEqual(
            purchase_order_line_3.last_qty_invoiced,
            0,
            msg="Last Invoiced Qty must be equal 0",
        )
        self.assertEqual(
            len(purchase_order_line_1.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal 2",
        )
        self.assertEqual(
            len(purchase_order_line_2.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal 2",
        )
        self.assertEqual(
            len(purchase_order_line_3.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal 2",
        )
        self.assertEqual(
            len(purchase_order.invoice_ids), 2, msg="Count Invoice must be equal 2"
        )

        self.assertEqual(
            len(purchase_order_line_1.component_ids),
            0,
            msg="Count components must be equal 0",
        )
        self.assertEqual(
            len(purchase_order_line_2.component_ids),
            0,
            msg="Count components must be equal 0",
        )
        self.assertEqual(
            len(purchase_order_line_3.component_ids),
            0,
            msg="Count components must be equal 0",
        )

        *_, invoice_line_1 = purchase_order_line_1.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_1.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            round(invoice_line_1.price_subtotal, 2), 20, msg="Subtotal must be equal 20"
        )
        *_, invoice_line_2 = purchase_order_line_2.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_2.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_line_2.price_subtotal, 40, msg="Subtotal must be equal 40"
        )
        *_, invoice_line_3 = purchase_order_line_3.invoice_lines.sorted("id")
        self.assertEqual(invoice_line_3.quantity, 2, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_line_3.price_subtotal, 60, msg="Subtotal must be equal 60"
        )
