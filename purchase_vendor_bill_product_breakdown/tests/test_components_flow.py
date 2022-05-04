from odoo.exceptions import UserError
from odoo.tests import Form, common


@common.tagged("post_install", "-at_install")
class TestComponentsFlow(common.TransactionCase):
    def setUp(self):
        super(TestComponentsFlow, self).setUp()
        ResPartner = self.env["res.partner"]
        ProductProduct = self.env["product.product"]
        ProductSupplierinfo = self.env["product.supplierinfo"]
        ProductSupplierinfoComponent = self.env["product.supplierinfo.component"]

        self.journal_id = (
            self.env["account.journal"]
            .create(
                {
                    "name": "TEST",
                    "type": "purchase",
                    "code": "TEST",
                    "company_id": self.env.user.company_id.id,
                }
            )
            .id
        )

        uom_unit_id = self.ref("uom.product_uom_unit")
        self.currency_id = self.env.ref("base.EUR").id

        self.res_partner_test_with_bill_components = ResPartner.create(
            {"name": "Partner #1", "bill_components": True}
        )

        self.res_partner_test_without_bill_components = ResPartner.create(
            {
                "name": "Partner #2",
                "bill_components": False,
            }
        )

        self.product_component_test_1 = ProductProduct.create(
            {
                "name": "Product Component #1",
                "standard_price": 1.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_component_test_2 = ProductProduct.create(
            {
                "name": "Product Component #2",
                "standard_price": 2.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_component_test_3 = ProductProduct.create(
            {
                "name": "Product Component #3",
                "standard_price": 3.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_test_1 = ProductProduct.create(
            {
                "name": "Product #1",
                "standard_price": 10.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_test_2 = ProductProduct.create(
            {
                "name": "Product #2",
                "standard_price": 20.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_product_test_3 = ProductProduct.create(
            {
                "name": "Product #3",
                "standard_price": 30.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_supplierinfo = ProductSupplierinfo.create(
            {
                "name": self.res_partner_test_with_bill_components.id,
                "product_id": self.product_product_test_1.id,
                "price": 1.0,
                "currency_id": self.currency_id,
            }
        )

        self.product_supplierinfo_component_test_1 = (
            ProductSupplierinfoComponent.create(
                {
                    "supplierinfo_id": self.product_supplierinfo.id,
                    "component_id": self.product_component_test_1.id,
                    "product_uom_qty": 1.0,
                    "product_uom_id": uom_unit_id,
                }
            )
        )

        self.product_supplierinfo_component_test_2 = (
            ProductSupplierinfoComponent.create(
                {
                    "supplierinfo_id": self.product_supplierinfo.id,
                    "component_id": self.product_component_test_2.id,
                    "product_uom_qty": 2.0,
                    "product_uom_id": uom_unit_id,
                }
            )
        )

        self.product_supplierinfo_component_test_3 = (
            ProductSupplierinfoComponent.create(
                {
                    "supplierinfo_id": self.product_supplierinfo.id,
                    "component_id": self.product_component_test_3.id,
                    "product_uom_qty": 3.0,
                    "product_uom_id": uom_unit_id,
                }
            )
        )

        self.product_supplierinfo.write(
            {
                "component_ids": [
                    (4, self.product_supplierinfo_component_test_1.id),
                    (4, self.product_supplierinfo_component_test_2.id),
                    (4, self.product_supplierinfo_component_test_3.id),
                ]
            }
        )

        self.product_product_test_1.write(
            {"seller_ids": [(6, 0, self.product_supplierinfo.ids)]}
        )

        self.product_additional_component_test_1 = ProductProduct.create(
            {
                "name": "Additional Component #1",
                "standard_price": 100.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

        self.product_additional_component_test_2 = ProductProduct.create(
            {
                "name": "Additional Component #2",
                "standard_price": 200.0,
                "type": "consu",
                "uom_id": uom_unit_id,
            }
        )

    def test_request_for_quotation_flow_with_components(self):
        PurchaseOrder = self.env["purchase.order"]

        purchase_order = Form(PurchaseOrder)
        purchase_order.partner_id = self.res_partner_test_with_bill_components
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 5
            line.price_unit = 10.0
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_2
            line.product_qty = 5
            line.price_unit = 20.0
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_3
            line.product_qty = 5
            line.price_unit = 30.0
        purchase_order = purchase_order.save()
        purchase_order.button_confirm()

        self.assertTrue(
            purchase_order.bill_components,
            msg="Purchase Order Vendor Bill Breakdown must be equal True",
        )

        purchase_order_line_1 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_1
        )
        self.assertEqual(
            len(purchase_order_line_1.component_ids),
            3,
            msg="Count components must be equal 3",
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            0,
            msg="Qty invoiced for components must be equal 0",
        )

        purchase_order_line_2 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_2
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

        purchase_order_line_3 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_3
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

        view_id = self.ref(
            "purchase_vendor_bill_product_breakdown.purchase_order_line_components_form_view"
        )
        purchase_order_line = Form(purchase_order_line_2, view=view_id)
        with purchase_order_line.component_ids.new() as line:
            line.component_id = self.product_additional_component_test_1
            line.product_uom_qty = 3
        with purchase_order_line.component_ids.new() as line:
            line.component_id = self.product_additional_component_test_2
            line.product_uom_qty = 2
        purchase_order_line.save()

        self.assertEqual(
            len(purchase_order_line_2.component_ids),
            2,
            msg="Count components must be equal 2",
        )
        with self.assertRaises(
            UserError, msg="Action must be raised UserError exception"
        ):
            purchase_order.action_create_invoice()

        purchase_order.order_line.write({"qty_received": 3})

        pol_1_component_1 = purchase_order_line_1.component_ids.filtered(
            lambda l: l.component_id == self.product_component_test_1
        )
        self.assertEqual(
            pol_1_component_1.total_qty, 3, msg="Component total Qty must be equal 3"
        )

        pol_1_component_2 = purchase_order_line_1.component_ids.filtered(
            lambda l: l.component_id == self.product_component_test_2
        )
        self.assertEqual(
            pol_1_component_2.total_qty, 6, msg="Component total Qty must be equal 6"
        )

        pol_1_component_3 = purchase_order_line_1.component_ids.filtered(
            lambda l: l.component_id == self.product_component_test_3
        )
        self.assertEqual(
            pol_1_component_3.total_qty, 9, msg="Component total Qty must be equal 9"
        )

        pol_2_component_1 = purchase_order_line_2.component_ids.filtered(
            lambda l: l.component_id == self.product_additional_component_test_1
        )
        self.assertEqual(
            pol_2_component_1.total_qty, 9, msg="Component total Qty must be equal 9"
        )

        pol_2_component_2 = purchase_order_line_2.component_ids.filtered(
            lambda l: l.component_id == self.product_additional_component_test_2
        )
        self.assertEqual(
            pol_2_component_2.total_qty, 6, msg="Component total Qty must be equal 6"
        )

        pol_1_component_1.total_qty += 1.52

        self.assertEqual(
            pol_1_component_1.total_qty,
            4.52,
            msg="Component total Qty must be equal 4.52",
        )
        purchase_order.action_create_invoice()

        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_1.last_qty_invoiced,
            3,
            msg="Last Invoiced Qty must be equal 3",
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_2.last_qty_invoiced,
            3,
            msg="Last Invoiced Qty must be equal 3",
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
            3,
            msg="Count elements in invoice by order line must be equal 3",
        )
        self.assertEqual(
            len(purchase_order_line_2.invoice_lines),
            2,
            msg="Count elements in invoice by order line must be equal 2",
        )
        self.assertEqual(
            len(purchase_order_line_3.invoice_lines),
            1,
            msg="Count elements in invoice by order line must be equal 1",
        )
        self.assertEqual(
            len(purchase_order.invoice_ids), 1, msg="Count Invoice must be equal 1"
        )

        invoice_1_line_1 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_1
        )
        self.assertEqual(
            round(invoice_1_line_1.quantity, 2), 4.52, msg="Qty must be equal 4.52"
        )
        self.assertEqual(
            invoice_1_line_1.price_unit, 1.0, msg="Unit Price must be equal 1"
        )
        self.assertEqual(
            round(invoice_1_line_1.price_subtotal, 2),
            4.52,
            msg="Subtotal must be equal 45.2",
        )

        invoice_1_line_2 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_2
        )
        self.assertEqual(invoice_1_line_2.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_1_line_2.price_unit, 2.0, msg="Unit price must be equal 2.0"
        )
        self.assertEqual(
            invoice_1_line_2.price_subtotal, 12, msg="Subtotal must be equal 12"
        )

        invoice_1_line_3 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_3
        )
        self.assertEqual(invoice_1_line_3.quantity, 9, msg="Qty must be equal 9")
        self.assertEqual(
            invoice_1_line_3.price_unit, 3.0, msg="Unit price must be equal 3.0"
        )
        self.assertEqual(
            invoice_1_line_3.price_subtotal, 27, msg="Subtotal must be equal 27"
        )

        invoice_2_line_1 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_additional_component_test_1
        )
        self.assertEqual(invoice_2_line_1.quantity, 9, msg="Qty must be equal 9")
        self.assertEqual(
            invoice_2_line_1.price_unit, 100, msg="Unit price must be equal 100"
        )
        self.assertEqual(
            invoice_2_line_1.price_subtotal, 900, msg="Subtotal must be equal 900"
        )

        invoice_2_line_2 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_additional_component_test_2
        )
        self.assertEqual(invoice_2_line_2.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_2_line_2.price_unit, 200, msg="Unit price must be equal 200"
        )
        self.assertEqual(
            invoice_2_line_2.price_subtotal, 1200, msg="Subtotal must be equal 1200"
        )

        invoice_3_line_1 = purchase_order_line_3.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_3
        )
        self.assertEqual(invoice_3_line_1.quantity, 3, msg="Qty must be equal 3")
        self.assertEqual(
            invoice_3_line_1.price_unit, 30, msg="Unit price must be equal 30"
        )
        self.assertEqual(
            invoice_3_line_1.price_subtotal, 90, msg="Subtotal must be equal 90"
        )

        self.assertEqual(
            purchase_order_line_1.qty_received, 3, msg="Received Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_1.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_2.qty_received, 3, msg="Received Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_2.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_3.qty_received, 3, msg="Received Qty must be equal 3"
        )
        self.assertEqual(
            purchase_order_line_3.qty_invoiced, 3, msg="Invoiced Qty must be equal 3"
        )
        self.assertEqual(
            round(pol_1_component_1.qty_invoiced, 2),
            4.52,
            msg="Invoiced Qty must be equal 4.52",
        )
        self.assertEqual(
            pol_1_component_2.qty_invoiced, 6, msg="Invoiced Qty must be equal 6"
        )
        self.assertEqual(
            pol_1_component_3.qty_invoiced, 9, msg="Invoiced Qty must be equal 9"
        )
        self.assertEqual(
            pol_2_component_1.qty_invoiced, 9, msg="Invoiced Qty must be equal 9"
        )
        self.assertEqual(
            pol_2_component_2.qty_invoiced, 6, msg="Invoiced Qty must be equal 6"
        )

        purchase_order.order_line.write({"qty_received": 5})
        self.assertEqual(
            round(pol_1_component_1.total_qty, 2),
            6.52,
            msg="Component total Qty must be equal 6.52",
        )
        self.assertEqual(
            pol_1_component_2.total_qty, 10, msg="Component total Qty must be equal 10"
        )
        self.assertEqual(
            pol_1_component_3.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_1.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_2.total_qty, 10, msg="Component total Qty must be equal 10"
        )

        purchase_order.action_create_invoice()

        self.assertEqual(
            len(purchase_order.invoice_ids), 2, msg="Count Invoice must be equal 2"
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
            6,
            msg="Count elements in invoice by order line must be equal 6",
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

        invoice_1_line_1 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_1
            and l.id != invoice_1_line_1.id
        )
        self.assertEqual(
            round(invoice_1_line_1.quantity, 2), 2, msg="Qty must be equal 2"
        )
        self.assertEqual(
            round(invoice_1_line_1.price_subtotal, 2), 2, msg="Subtotal must be equal 2"
        )

        invoice_1_line_2 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_2
            and l.id != invoice_1_line_2.id
        )
        self.assertEqual(invoice_1_line_2.quantity, 4, msg="Qty must be equal 4")
        self.assertEqual(
            invoice_1_line_2.price_subtotal, 8, msg="Subtotal must be equal 8"
        )

        invoice_1_line_3 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_component_test_3
            and l.id != invoice_1_line_3.id
        )
        self.assertEqual(invoice_1_line_3.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_1_line_3.price_subtotal, 18, msg="Subtotal must be equal 18"
        )

        invoice_2_line_1 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_additional_component_test_1
            and l.id != invoice_2_line_1.id
        )
        self.assertEqual(invoice_2_line_1.quantity, 6, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_2_line_1.price_subtotal, 600, msg="Subtotal must be equal 600"
        )

        invoice_2_line_2 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_additional_component_test_2
            and l.id != invoice_2_line_2.id
        )
        self.assertEqual(invoice_2_line_2.quantity, 4, msg="Qty must be equal 4")
        self.assertEqual(
            invoice_2_line_2.price_subtotal, 800, msg="Subtotal must be equal 800"
        )

        invoice_3_line_1 = purchase_order_line_3.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_3
            and l.id != invoice_3_line_1.id
        )
        self.assertEqual(invoice_3_line_1.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_3_line_1.price_subtotal, 60, msg="Subtotal must be equal 60"
        )
        self.assertEqual(
            round(pol_1_component_1.total_qty, 2),
            6.52,
            msg="Component total Qty must be equal 6.52",
        )
        self.assertEqual(
            pol_1_component_2.total_qty, 10, msg="Component total Qty must be equal 10"
        )
        self.assertEqual(
            pol_1_component_3.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_1.total_qty, 15, msg="Component total Qty must be equal 15"
        )
        self.assertEqual(
            pol_2_component_2.total_qty, 10, msg="Component total Qty must be equal 10"
        )

    def test_request_for_quotation_flow_without_components(self):
        PurchaseOrder = self.env["purchase.order"]

        purchase_order = Form(PurchaseOrder)
        purchase_order.partner_id = self.res_partner_test_without_bill_components
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.product_qty = 5
            line.price_unit = 10.0
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_2
            line.product_qty = 5
            line.price_unit = 20.0
        with purchase_order.order_line.new() as line:
            line.product_id = self.product_product_test_3
            line.product_qty = 5
            line.price_unit = 30.0
        purchase_order = purchase_order.save()
        purchase_order.button_confirm()

        self.assertFalse(
            purchase_order.bill_components,
            msg="Purchase Order Vendor Bill Breakdown must be equal True",
        )

        purchase_order_line_1 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_1
        )
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

        purchase_order_line_2 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_2
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

        purchase_order_line_3 = purchase_order.order_line.filtered(
            lambda l: l.product_id == self.product_product_test_3
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

        invoice_line_1 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_1
        )
        self.assertEqual(invoice_line_1.quantity, 3, msg="Qty must be equal 2")
        self.assertEqual(
            round(invoice_line_1.price_subtotal, 2), 30, msg="Subtotal must be equal 30"
        )

        invoice_line_2 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_2
        )
        self.assertEqual(invoice_line_2.quantity, 3, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_line_2.price_subtotal, 60, msg="Subtotal must be equal 60"
        )

        invoice_line_3 = purchase_order_line_3.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_3
        )
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

        invoice_line_1 = purchase_order_line_1.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_1
            and l.id != invoice_line_1.id
        )
        self.assertEqual(invoice_line_1.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            round(invoice_line_1.price_subtotal, 2), 20, msg="Subtotal must be equal 20"
        )

        invoice_line_2 = purchase_order_line_2.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_2
            and l.id != invoice_line_2.id
        )
        self.assertEqual(invoice_line_2.quantity, 2, msg="Qty must be equal 2")
        self.assertEqual(
            invoice_line_2.price_subtotal, 40, msg="Subtotal must be equal 40"
        )

        invoice_line_3 = purchase_order_line_3.invoice_lines.filtered(
            lambda l: l.product_id == self.product_product_test_3
            and l.id != invoice_line_3.id
        )
        self.assertEqual(invoice_line_3.quantity, 2, msg="Qty must be equal 6")
        self.assertEqual(
            invoice_line_3.price_subtotal, 60, msg="Subtotal must be equal 60"
        )
