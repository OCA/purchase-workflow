# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseInvoicePlanExpand(TransactionCase):
    def setUp(self):
        super(TestPurchaseInvoicePlanExpand, self).setUp()
        # Create a PO
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_product = self.env.ref("product.product_product_2")
        self.test_product.purchase_method = "purchase"

        self.test_po = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Service",
                            "product_id": self.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 500,
                        },
                    )
                ],
            }
        )

    def test_invoice_plan_expand(self):
        ctx = {
            "active_id": self.test_po.id,
            "active_ids": [self.test_po.id],
            "all_remain_invoices": True,
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 3
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        # Do expand
        insallment_group = {1: "FY2020", 2: "FY2020", 3: "FY2021"}
        for plan in self.test_po.invoice_plan_ids:
            plan.expand_group = insallment_group[plan.installment]
        self.test_po.write({"expand": True})
        self.assertEqual(len(self.test_po.order_line), 2)
        fy2020 = self.test_po.order_line.filtered_domain(
            [("expand_group", "=", "FY2020")]
        )
        fy2021 = self.test_po.order_line.filtered_domain(
            [("expand_group", "=", "FY2021")]
        )
        self.assertEqual(fy2020.product_qty, 0.67)
        self.assertEqual(fy2021.product_qty, 0.33)
        # Create all invoices by plan
        self.test_po.button_confirm()
        self.assertEqual(self.test_po.state, "purchase")
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(ctx).create_invoices_by_plan()
        self.assertEqual(len(self.test_po.invoice_ids), 3)
        sum_invoice_qty = sum(
            self.test_po.invoice_ids.mapped("invoice_line_ids").mapped("quantity")
        )
        self.assertEqual(sum_invoice_qty, 1)

    def test_invoice_plan_expand_merge(self):
        ctx = {
            "active_id": self.test_po.id,
            "active_ids": [self.test_po.id],
            "all_remain_invoices": True,
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 3
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        # Do expand
        insallment_group = {1: "FY2020", 2: "FY2020", 3: "FY2021"}
        for plan in self.test_po.invoice_plan_ids:
            plan.expand_group = insallment_group[plan.installment]
        self.test_po.write({"expand": True})
        self.assertEqual(len(self.test_po.order_line), 2)
        # Do merge
        self.test_po.write({"expand": False})
        self.assertEqual(len(self.test_po.order_line), 1)
