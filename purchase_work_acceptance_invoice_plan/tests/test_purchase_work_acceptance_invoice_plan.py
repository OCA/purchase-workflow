# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseWorkAcceptanceInvoicePlan(TransactionCase):
    def setUp(self):
        super(TestPurchaseWorkAcceptanceInvoicePlan, self).setUp()
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.WaInstallment = self.env["select.work.acceptance.invoice.plan.wizard"]
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

    def test_wizard_wa_installment(self):
        purchase_order = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 2
        purchase_plan = p.save()
        purchase_plan.with_context(purchase_order).purchase_create_invoice_plan()
        invoice_plan = self.test_po_product.invoice_plan_ids
        self.test_po_product.button_confirm()
        wizard = (
            self.env["select.work.acceptance.invoice.plan.wizard"]
            .with_context(purchase_order)
            .create({"installment_id": invoice_plan[0].id})
        )
        wizard._compute_active_installment_ids()
        res = wizard.button_create_wa()
        ctx = res.get("context")
        work_acceptance = Form(self.env["work.acceptance"].with_context(ctx))
        self.assertEqual(work_acceptance.state, "draft")
