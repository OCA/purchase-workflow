# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form

from .common import TestPurchaseInvoicePlanCommon


class TestPurchaseInvoicePlan(TestPurchaseInvoicePlanCommon):
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
        receive = self.test_po_product.picking_ids.filtered(
            lambda pick: pick.state != "done"
        )
        receive.move_ids.quantity = 10.0
        receive.button_validate()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(**ctx).create_invoices_by_plan()
        self.assertEqual(
            self.test_po_product.amount_total,
            sum(self.test_po_product.invoice_ids.mapped("amount_total")),
        )
        for plan in self.test_po_product.invoice_plan_ids:
            self.assertEqual(len(plan.invoice_ids), 1)
            self.assertEqual(plan.invoice_ids.invoice_date, plan.plan_date)
            self.assertEqual(plan.amount_invoiced, plan.invoice_ids.amount_untaxed)

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
        with (
            self.assertRaises(ValidationError) as e,
            Form(self.PurchaseInvoicePlan) as p,
        ):
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
        receive = self.test_po_product.picking_ids.filtered(
            lambda pick: pick.state != "done"
        )
        receive.move_ids.quantity = 1.0
        # receive.button_validate()
        backorder_wizard_dict = receive.button_validate()
        backorder_wizard = Form(
            self.env[backorder_wizard_dict["res_model"]].with_context(
                **backorder_wizard_dict["context"]
            )
        ).save()
        backorder_wizard.process()
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
        self.assertIn(self.test_po_product.name, first_install.display_name)
        self.assertIn("Invoice Plan", first_install.display_name)
        self.test_po_product.invoice_plan_ids[4].amount = 3000
        self.test_po_product.button_confirm()
        self.assertEqual(self.test_po_product.state, "purchase")
        # Receive all products
        receive = self.test_po_product.picking_ids.filtered(
            lambda pick: pick.state != "done"
        )
        receive.move_ids.quantity = 10.0
        receive.button_validate()
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
                            "uom_id": self.test_product.uom_id.id,
                            "price_unit": 1000,
                            "tax_ids": False,
                        },
                    )
                ],
            }
        )
        # Overall amount changed to 11000, install amount not changed, only percent
        # changed.
        self.assertEqual(self.test_po_product.amount_total, 11000)
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

    def test_invoice_plan_keeps_sections(self):
        """Bills created from PO keep section lines, only product lines
        get the planned quantity"""
        ctx = {
            "active_id": self.test_po_product.id,
            "active_ids": [self.test_po_product.id],
            "all_remain_invoices": False,
        }
        self.test_po_product.order_line = [
            Command.create(
                {
                    "name": "Section",
                    "display_type": "line_section",
                    "product_qty": 0,
                    "sequence": 1,
                }
            ),
        ]
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = 2
        purchase_plan = p.save()
        purchase_plan.with_context(**ctx).purchase_create_invoice_plan()
        self.test_po_product.button_confirm()
        receive = self.test_po_product.picking_ids.filtered(
            lambda pick: pick.state != "done"
        )
        receive.move_ids.quantity = 10.0
        receive.button_validate()
        purchase_create = self.env["purchase.make.planned.invoice"].create({})
        purchase_create.with_context(**ctx).create_invoices_by_plan()
        invoice_lines = self.test_po_product.invoice_ids.invoice_line_ids
        self.assertEqual(
            invoice_lines.mapped("display_type"),
            ["line_section", "product"],
        )
        product_line = invoice_lines.filtered(lambda ln: ln.display_type == "product")
        self.assertEqual(product_line.quantity, 5)

    def test_to_invoice_multi_purchase(self):
        """Purchase orders confirmed together have each their next installment"""
        purchases = self.test_po_product | self._create_plan_purchase()
        self.test_po_product.create_invoice_plan(5, fields.Date.today(), 1, "month")
        purchases.button_confirm()
        for purchase in purchases:
            self.assertEqual(
                purchase.invoice_plan_ids.mapped("to_invoice"),
                [True, False, False, False, False],
            )

    def test_zero_amount_purchase(self):
        """Installment billed on a purchase order without amount"""
        purchase = self._create_plan_purchase(price_unit=0)
        purchase.button_confirm()
        receive = purchase.picking_ids
        receive.move_ids.quantity = 10
        receive.button_validate()
        self._create_bill_by_plan(purchase)
        first = purchase.invoice_plan_ids[0]
        self.assertTrue(first.invoiced)
        self.assertEqual(first.amount, 0)
        self.assertEqual(first.percent, 20)

    def test_check_percent(self):
        """Installments are checked when written directly"""
        self.test_po_product.create_invoice_plan(5, fields.Date.today(), 1, "month")
        plans = self.test_po_product.invoice_plan_ids
        with self.assertRaises(UserError):
            plans[0].percent = 20.2
        with self.assertRaises(ValidationError):
            plans[0].percent = -10
        plans[0].percent = 20.004
        # Installments changed together from the order form
        self.test_po_product.write(
            {
                "invoice_plan_ids": [
                    Command.update(plans[2].id, {"percent": 30}),
                    Command.update(plans[3].id, {"percent": 10}),
                ]
            }
        )
        with self.assertRaises(UserError):
            self.test_po_product.write(
                {"invoice_plan_ids": [Command.update(plans[2].id, {"percent": 40})]}
            )
        with self.assertRaises(ValidationError):
            self.test_po_product.write(
                {
                    "invoice_plan_ids": [
                        Command.update(plans[2].id, {"percent": -10}),
                        Command.update(plans[3].id, {"percent": 50}),
                    ]
                }
            )
        self.test_po_product.button_confirm()
        with self.assertRaises(ValidationError):
            plans[1].percent = 0

    def test_invoice_more_than_plan(self):
        """Bill edited over its installment is accepted, as in the standard"""
        self.test_po_product.create_invoice_plan(5, fields.Date.today(), 1, "month")
        self.test_po_product.button_confirm()
        receive = self.test_po_product.picking_ids
        receive.move_ids.quantity = 10
        receive.button_validate()
        self._create_bill_by_plan(self.test_po_product)
        first = self.test_po_product.invoice_plan_ids[0]
        first.invoice_ids.invoice_line_ids.quantity = 4
        self.assertEqual(first.percent, 40)
        self.assertEqual(self.test_po_product.ip_total_percent, 120)

    def test_multi_company(self):
        """Installments of another company are not accessible"""
        company = self.env["res.company"].sudo().create({"name": "Other Company"})
        purchase = self._create_plan_purchase(company=company)
        # New company is given to its creator
        self.env.user.sudo().company_ids -= company
        self.env.invalidate_all()
        plans = self.env["purchase.invoice.plan"].search(
            [("purchase_id", "=", purchase.id)]
        )
        self.assertFalse(plans)
        with self.assertRaises(AccessError):
            self._create_bill_by_plan(purchase)
