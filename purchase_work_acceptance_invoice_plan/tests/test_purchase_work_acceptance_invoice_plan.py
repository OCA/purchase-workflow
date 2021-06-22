# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseWorkAcceptanceInvoicePlan(TransactionCase):
    def setUp(self):
        super(TestPurchaseWorkAcceptanceInvoicePlan, self).setUp()
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseInvoicePlan = self.env["purchase.create.invoice.plan"]
        self.WaInstallmentWizard = self.env[
            "select.work.acceptance.invoice.plan.wizard"
        ]
        self.WaInvoiceWizard = self.env["select.work.acceptance.wizard"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_service = self.env.ref("product.product_product_2")
        self.test_product = self.env.ref("product.product_product_7")
        self.test_product.purchase_method = "purchase"
        self.date_now = fields.Datetime.now()
        # Method create wa
        self.apply_all = self.env.ref(
            "purchase_work_acceptance_invoice_plan.apply_on_all_product_line"
        )
        self.apply_match_amount = self.env.ref(
            "purchase_work_acceptance_invoice_plan.apply_on_matched_amount"
        )
        # Enable and Config WA
        self.env["res.config.settings"].create(
            {
                "group_enable_wa_on_po": True,
                "group_enable_wa_on_in": True,
                "group_enable_wa_on_invoice": True,
            }
        ).execute()

    def _create_purchase_order(self, product):
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "name": product.name,
                            "price_unit": product.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 10,
                        },
                    )
                ],
            }
        )
        return purchase_order

    def test_01_purchase_invoice_plan_to_wa(self):
        purchase_order = self._create_purchase_order(self.test_product)
        ctx = {
            "active_id": purchase_order.id,
            "active_ids": [purchase_order.id],
        }
        # Create purchase plan
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 2
        purchase_plan = p.save()
        purchase_plan.with_context(ctx).purchase_create_invoice_plan()
        invoice_plan = purchase_order.invoice_plan_ids
        # Check invoice plan can editable
        self.assertFalse(invoice_plan[0].no_edit)
        purchase_order.button_confirm()
        # Check create wa with last invoice plan, it should warning
        wa_installment = self.WaInstallmentWizard.with_context(ctx).create(
            {"installment_id": invoice_plan[1].id}
        )
        check_installment = wa_installment._onchange_installment_id()
        self.assertTrue(check_installment.get("warning"))
        # Check select base on match amount, it not found and raise error
        with self.assertRaises(UserError):
            with Form(self.WaInstallmentWizard.with_context(ctx)) as wa_wizard:
                wa_wizard.installment_id = invoice_plan[0]
                wa_wizard.apply_method_id = self.apply_match_amount
        with Form(self.WaInstallmentWizard.with_context(ctx)) as wa_wizard:
            wa_wizard.installment_id = invoice_plan[0]
            wa_wizard.apply_method_id = self.apply_all
        wizard = wa_wizard.save()
        self.assertTrue(wizard.wa_qty_line_ids)
        self.assertEqual(wizard.wa_qty_line_ids.quantity, 5.0)
        # Check create wa with po line zero amount, it should error
        price_subtotal = wizard.order_line_ids.price_subtotal
        qty_to_accept = wizard.order_line_ids.qty_to_accept
        installment_amount = wizard.installment_id.amount
        with self.assertRaises(UserError):
            wizard.order_line_ids.price_subtotal = 0.0
            wizard._compute_wa_qty_line_ids()
        wizard.order_line_ids.price_subtotal = price_subtotal
        # Check installment amount is zero, it wa qty should zero too (deposit)
        wizard.installment_id.amount = 0.0
        wizard._compute_wa_qty_line_ids()
        self.assertEqual(wizard.wa_qty_line_ids.quantity, 0.0)
        wizard.installment_id.amount = installment_amount
        # Check add qty over po, it will change to not over qty
        wizard.order_line_ids.qty_to_accept = 1
        wizard._compute_wa_qty_line_ids()
        self.assertEqual(wizard.wa_qty_line_ids.quantity, 1.0)
        wizard.order_line_ids.qty_to_accept = qty_to_accept
        wizard._compute_wa_qty_line_ids()
        res = wizard.button_create_wa()
        # Check Work Acceptance
        ctx_wa = res.get("context")
        work_acceptance = Form(self.env["work.acceptance"].with_context(ctx_wa))
        wa = work_acceptance.save()
        self.assertEqual(wa.state, "draft")
        purchase_order.action_view_wa()
        self.assertEqual(purchase_order.wa_count, 1)
        wa.button_accept()
        self.assertEqual(wa.state, "accept")
        # Check create wa duplicate, it will error
        wa_installment = self.WaInstallmentWizard.with_context(ctx_wa).create(
            {"installment_id": invoice_plan[0].id}
        )
        with self.assertRaises(UserError):
            wa_installment.button_create_wa()

        # Received Products
        picking = purchase_order.picking_ids[0]
        self.assertEqual(len(picking.move_ids_without_package), 1)
        with Form(picking) as p:
            p.wa_id = wa
        p.save()
        picking.move_ids_without_package[0].quantity_done = 5.0
        picking.button_validate()
        # Create invoice following wa
        with Form(self.WaInvoiceWizard.with_context(ctx)) as wa_inv_wizard:
            wa_inv_wizard.wa_id = wa
        wiz = wa_inv_wizard.save()
        res = wiz.button_create_vendor_bill()
        invoice = self.env["account.move"].browse(res["res_id"])
        self.assertEqual(sum(invoice.invoice_line_ids.mapped("quantity")), 5.0)
        self.assertEqual(invoice.wa_id, wa)
