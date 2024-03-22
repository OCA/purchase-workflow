# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

import odoo.exceptions
from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestPurchaseReturnOrder(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseReturnOrder, cls).setUpClass()
        uom_unit = cls.env.ref("uom.product_uom_unit")
        uom_hour = cls.env.ref("uom.product_uom_hour")
        returns_account = cls.env["account.account"].create(
            {
                "name": "Vendor Returns",
                "code": "VR01",
                "account_type": "income",
            }
        )
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PROD_ORDER",
                "taxes_id": False,
                "property_account_vendor_return_id": returns_account.id,
            }
        )
        cls.service_order = cls.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "standard_price": 40.0,
                "list_price": 90.0,
                "type": "service",
                "uom_id": uom_hour.id,
                "uom_po_id": uom_hour.id,
                "purchase_method": "purchase",
                "default_code": "PRE-PAID",
                "taxes_id": False,
                "property_account_vendor_return_id": returns_account.id,
            }
        )

    # Test a product ordered with refund only option
    def test_01(self):
        # Create a Purchase Return Order
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": True,
                "taxes_id": False,
                "display_type": "product",
            }
        )
        self.assertEqual(purchase_return_order.invoice_status, "no")
        purchase_return_order.button_confirm()

        self.assertEqual(purchase_return_order.invoice_status, "to invoice")
        for line in purchase_return_order.order_line:
            self.assertEqual(line.product_qty, 10)
            self.assertEqual(line.qty_invoiced, 0.0)
        purchase_return_order.action_create_refund()
        self.assertEqual(purchase_return_order.invoice_status, "invoiced")

    # Test a product ordered without refund only option
    def test_02(self):
        # Create a Purchase Return Order- not refund only
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
                "display_type": "product",
            }
        )
        self.assertEqual(purchase_return_order.invoice_status, "no")
        purchase_return_order.button_confirm()
        self.assertEqual(purchase_return_order.invoice_status, "to invoice")

    # Test a service ordered with refund only option
    def test_03(self):
        # Create Purchase Return Order of a service that is ordered WITH refund only
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.service_order.name,
                "product_id": self.service_order.id,
                "product_qty": 10.0,
                "product_uom": self.service_order.uom_id.id,
                "price_unit": self.service_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": True,
                "taxes_id": False,
                "display_type": "product",
            }
        )
        self.assertEqual(purchase_return_order.state, "draft")
        self.assertEqual(purchase_return_order.invoice_status, "no")
        purchase_return_order.button_confirm()
        self.assertEqual(purchase_return_order.invoice_status, "to invoice")
        self.assertEqual(purchase_return_order.state, "purchase")

    # Test state for any purchase return order and return back to draft
    def test_04(self):
        # Create a Purchase Return Order
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
            }
        )
        self.assertEqual(purchase_return_order.state, "draft")
        # In the initial draft status there's nothing to refund
        self.assertEqual(purchase_return_order.invoice_status, "no")
        # Check that the order has been created and is in the correct state
        purchase_return_order.button_confirm()
        self.assertEqual(purchase_return_order.state, "purchase")
        purchase_return_order.button_draft()
        self.assertEqual(purchase_return_order.state, "draft")

    # Test to create a vendor bill and its associated state
    def test_05(self):
        # Create a Purchase Return Order
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create({"partner_id": self.partner_a.id})
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
            }
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
                "display_type": "product",
            }
        )
        purchase_return_order.button_confirm()
        purchase_return_order.action_create_refund()
        invoice = purchase_return_order.mapped("order_line.invoice_lines.move_id")
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, "draft")
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    # Test to check if a ValiadationError is thrown when changing the company to
    #  another one that is not the product's
    def test_06(self):
        try:
            company_a = self.env["res.company"].create(
                {
                    "name": "Company A",
                }
            )
            company_b = self.env["res.company"].create(
                {
                    "name": "Company B",
                }
            )
            purchase_return_order = (
                self.env["purchase.return.order"]
                .with_context(tracking_disable=True)
                .create(
                    {
                        "partner_id": self.partner_a.id,
                        "company_id": company_b.id,
                    }
                )
            )
            self.product_order.company_id = company_b.id
            PurchaseReturnOrderLine = (
                self.env["purchase.return.order.line"]
                .with_context(tracking_disable=True)
                .create(
                    {
                        "name": self.product_order.name,
                        "product_id": self.product_order.id,
                        "product_qty": 10.0,
                        "product_uom": self.product_order.uom_id.id,
                        "price_unit": self.product_order.list_price,
                        "order_id": purchase_return_order.id,
                        "refund_only": False,
                        "taxes_id": False,
                        "company_id": company_b.id,
                        "display_type": "product",
                    }
                )
            )
            purchase_return_order.company_id = company_a.id
            PurchaseReturnOrderLine.company_id = company_a.id
        except odoo.exceptions.ValidationError:
            return
        else:
            self.fail(
                "ValidationError was not raised when attempting to change"
                "the company return order to one different to the product"
                "in the product line"
            )

    # Test to make sure that when the date planned of a purchase return order is changed,
    # so are the date_planned of the products.
    def test_07(self):
        testDate = datetime.strptime("07/28/2014 18:54:55.099", "%m/%d/%Y %H:%M:%S.%f")
        purchase_return_order = (
            self.env["purchase.return.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        PurchaseReturnOrderLine = self.env["purchase.return.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
            }
        )
        PurchaseReturnOrderLine.create(
            {
                "name": self.service_order.name,
                "product_id": self.service_order.id,
                "product_qty": 10.0,
                "product_uom": self.service_order.uom_id.id,
                "price_unit": self.service_order.list_price,
                "order_id": purchase_return_order.id,
                "refund_only": False,
                "taxes_id": False,
            }
        )
        purchase_return_order.date_planned = testDate
        for line in purchase_return_order:
            self.assertEqual(line.date_planned, testDate)
