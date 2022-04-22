# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestInvoicePlanSelection(TransactionCase):
    def setUp(self):
        super(TestInvoicePlanSelection, self).setUp()
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.MakeInvoice = self.env["purchase.make.planned.invoice"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_service = self.env.ref("product.product_product_2")
        self.test_base_on_all_line = self.env.ref(
            "purchase_invoice_plan_selection.apply_on_all_product_line"
        )

        self.test_po_service = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Service-1",
                            "product_id": self.test_service.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": self.test_service.uom_id.id,
                            "price_unit": 500,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "PO-Service-2",
                            "product_id": self.test_service.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": self.test_service.uom_id.id,
                            "price_unit": 1000,
                        },
                    ),
                ],
            }
        )

    def test_create_invoice_by_manual_selection(self):
        ctx = {
            "active_id": self.test_po_service.id,
            "active_ids": [self.test_po_service.id],
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 2  # 50% each
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        invoice_plan = self.test_po_service.invoice_plan_ids
        self.test_po_service.button_confirm()
        self.test_po_service.order_line.write({"qty_received": 1})  # receive service
        # Create 1st installment
        with Form(self.MakeInvoice.with_context(ctx)) as f:
            f.next_bill_method = "manual"
            f.installment_id = invoice_plan[0]
            f.apply_method_id = self.test_base_on_all_line
        wizard = f.save()
        # Test line quantity
        self.assertEqual(wizard.invoice_qty_line_ids.mapped("quantity"), [0.5, 0.5])
        self.assertTrue(wizard.valid_amount)
        wizard.create_invoice_by_selection()
        self.assertEqual(sum(invoice_plan[0].invoice_ids.mapped("amount_total")), 750)
        # Create 2nd installment
        with Form(self.MakeInvoice.with_context(ctx)) as f:
            f.next_bill_method = "manual"
            f.installment_id = invoice_plan[1]
            f.apply_method_id = self.test_base_on_all_line
        wizard = f.save()
        self.assertEqual(wizard.invoice_qty_line_ids.mapped("quantity"), [0.5, 0.5])
        # Manually set all qty to 0.25 instead of 0.5
        wizard.invoice_qty_line_ids.write({"quantity": 0.25})
        self.assertFalse(wizard.valid_amount)
        wizard.create_invoice_by_selection()
        self.assertEqual(sum(invoice_plan[1].invoice_ids.mapped("amount_total")), 375)
