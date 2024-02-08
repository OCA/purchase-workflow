# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseInvoicePlan(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a PO
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseInvoicePlan = cls.env["purchase.create.invoice.plan"]
        cls.StockBackorderConfirm = cls.env["stock.backorder.confirmation"]
        cls.StockPicking = cls.env["stock.picking"]

        cls.test_partner = cls.env.ref("base.res_partner_12")
        cls.test_service = cls.env.ref("product.product_product_2")
        cls.test_product = cls.env.ref("product.product_product_7")

        cls.test_po_service = cls.env["purchase.order"].create(
            {
                "partner_id": cls.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Service",
                            "product_id": cls.test_service.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": cls.test_service.uom_id.id,
                            "price_unit": 500,
                        },
                    )
                ],
            }
        )
        cls.test_po_product = cls.env["purchase.order"].create(
            {
                "partner_id": cls.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Product",
                            "product_id": cls.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 10,
                            "product_uom": cls.test_product.uom_id.id,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )

    def test_invoice_plan(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": True,
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 5
        purchase_plan = p.save()
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.test_po_product.invoice_plan_ids), 5)
        self.test_po_product.invoice_plan_ids[0].amount = 1000
        self.test_po_product.invoice_plan_ids[4].amount = 3000
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # Receive all products
        receive = self.test_po_product.picking_ids.filtered(lambda l: l.state != "done")
        receive.move_ids_without_package.quantity_done = 10.0
        receive._action_done()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(
            self.test_po_product.amount_total,
            sum(self.test_po_product.invoice_ids.mapped("amount_total")),
        )

    def test_unlink_invoice_plan(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
        }
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 5
        plan = p.save()
        plan.with_context(**ctx).purchase_create_invoice_plan()
        # Remove it
        self.test_po_product.remove_invoice_plan()
        self.assertFalse(self.test_po_product.invoice_plan_ids)

    def test_error(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": True,
        }
        # UserError Use Invoice Plan selected, but no plan created
        with self.assertRaises(UserError):
            self.test_po_product.button_confirm()
        # ValidationError Number of Installment <= 1
        with self.assertRaises(ValidationError) as e:
            with Form(self.PurchaseInvoicePlan) as p:
                p.num_installment = 0
                p.save()
        error_message = "Number Installment must greater than 1"
        self.assertEqual(e.exception.args[0], error_message)
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 5
        purchase_plan = p.save()
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        # Test exceed percent
        with self.assertRaises(UserError):
            self.test_po_product.invoice_plan_ids[0].percent = 99
            self.test_po_product._check_ip_total_percent()
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # UserError Please fill percentage for all invoice plan lines
        with self.assertRaises(UserError):
            for per in self.test_po_product.invoice_plan_ids:
                per.percent = 0
            self.test_po_product._check_invoice_plan()
        # Receive product 1 unit
        receive = self.test_po_product.picking_ids.filtered(lambda l: l.state != "done")
        receive.move_ids_without_package.quantity_done = 1.0
        receive._action_done()
        # ValidationError Create all invoice plan - Receive < Invoice require
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        with self.assertRaises(ValidationError) as e:
            purchase_create.with_context(**ctx).create_invoices_by_plan()
        error_message = (
            "Plan quantity: 2.0, exceed invoiceable quantity: 1.0"
            "\nProduct should be delivered before invoice"
        )
        self.assertEqual(e.exception.args[0], error_message)

    def test_invoice_plan_po_edit(self):
        """Case when some installment already invoiced,
        but then, the PO line added. Test to ensure that
        the invoiced amount of the done installment is fixed"""
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": False,
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 5
        purchase_plan = p.save()
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.test_po_product.invoice_plan_ids), 5)
        first_install = self.test_po_product.invoice_plan_ids[0]
        first_install.amount = 1000
        self.test_po_product.invoice_plan_ids[4].amount = 3000
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # Receive all products
        receive = self.test_po_product.picking_ids.filtered(lambda l: l.state != "done")
        receive.move_ids_without_package.quantity_done = 10.0
        receive._action_done()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        # Create only the 1st invoice, amount should be 1000, and percent is 10
        purchase_create.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(first_install.amount, 1000)
        self.assertEqual(first_install.percent, 10)
        # Add new PO line with amount = 1000, check that only percent is changed
        self.test_po_product.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Product-NEW",
                            "product_id": self.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )
        # Overall amount changed to 11000, install amount not changed, only percent changed.
        self.assertEqual(self.test_po_product.amount_total, 11000)
        self.test_po_product.invoice_plan_ids._compute_amount()
        self.assertEqual(first_install.amount, 1000)
        self.assertEqual(first_install.percent, 9.090909)
        with self.assertRaises(UserError):
            self.test_po_product.remove_invoice_plan()

    @freeze_time("2022-01-01")
    def test_next_date(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": False,
        }
        # Create purchase plan
        for item in ["day", "month", "year"]:
            with Form(self.PurchaseInvoicePlan) as p:
                p.num_installment = 5
                p.interval = 5
                p.interval_type = item
            purchase_plan = p.save()
            purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
            self.assertEqual(len(self.test_po_product.invoice_plan_ids), 5)
            self.test_po_product.remove_invoice_plan()
