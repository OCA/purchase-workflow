# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseInvoicePlan(TransactionCase):
    def setUp(self):
        super(TestPurchaseInvoicePlan, self).setUp()
        # Create a PO
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.StockBackorderConfirm = self.env["stock.backorder.confirmation"]
        self.StockPicking = self.env["stock.picking"]

        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_service = self.env.ref("product.product_product_2")
        self.test_product = self.env.ref("product.product_product_7")

        self.test_po_service = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Service",
                            "product_id": self.test_service.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": self.test_service.uom_id.id,
                            "price_unit": 500,
                        },
                    )
                ],
            }
        )
        self.test_po_product = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Product",
                            "product_id": self.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 10,
                            "product_uom": self.test_product.uom_id.id,
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
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
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
        purchase_create.with_context(ctx).create_invoices_by_plan()
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
        plan.with_context(ctx).purchase_create_invoice_plan()
        # Remove it
        self.test_po_product.remove_invoice_plan()
        self.assertFalse(self.test_po_product.invoice_plan_ids)

    def test_error(self):
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": True,
        }
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
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # Receive product 1 unit
        receive = self.test_po_product.picking_ids.filtered(lambda l: l.state != "done")
        receive.move_ids_without_package.quantity_done = 1.0
        receive._action_done()
        # ValidationError Create all invoice plan - Receive < Invoice require
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        with self.assertRaises(ValidationError) as e:
            purchase_create.with_context(ctx).create_invoices_by_plan()
        error_message = (
            "Plan quantity: 2.0, exceed invoiceable quantity: 1.0"
            "\nProduct should be delivered before invoice"
        )
        self.assertEqual(e.exception.args[0], error_message)
