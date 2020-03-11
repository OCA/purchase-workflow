# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseWorkAcceptance(TransactionCase):
    def setUp(self):
        super(TestPurchaseWorkAcceptance, self).setUp()
        # Create Product
        self.service_product = self.env.ref("product.product_product_1")
        self.product_product = self.env.ref("product.product_product_6")
        # Create Vendor
        self.res_partner = self.env.ref("base.res_partner_3")
        # Create Employee
        self.employee = self.env.ref("base.user_demo")
        # Create Date
        self.date_now = fields.Datetime.now()

    def test_00_wa_button(self):
        work_acceptance = self.env["work.acceptance"].create(
            {
                "partner_id": self.res_partner.id,
                "responsible_id": self.employee.id,
                "date_due": self.date_now,
                "date_receive": self.date_now,
                "company_id": self.env.ref("base.main_company").id,
                "wa_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_product.id,
                            "name": self.service_product.name,
                            "price_unit": self.service_product.standard_price,
                            "product_qty": 3.0,
                            "product_uom": self.service_product.uom_id.id,
                        },
                    )
                ],
            }
        )
        work_acceptance.button_accept()
        self.assertEqual(work_acceptance.state, "accept")
        work_acceptance.button_cancel()
        self.assertEqual(work_acceptance.state, "cancel")
        work_acceptance.button_draft()
        self.assertEqual(work_acceptance.state, "draft")

    def test_01_action_view_wa(self):
        # Create Purchase Order
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_product.id,
                            "product_uom": self.service_product.uom_id.id,
                            "name": self.service_product.name,
                            "price_unit": self.service_product.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 42.0,
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")

        res = purchase_order.with_context(create_wa=True).action_view_wa()
        ctx = res.get("context")
        work_acceptance = Form(self.env["work.acceptance"].with_context(ctx))
        self.assertEqual(work_acceptance.state, "draft")

    def test_02_flow_product(self):
        # Create Purchase Order
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product.id,
                            "product_uom": self.product_product.uom_id.id,
                            "name": self.product_product.name,
                            "price_unit": self.product_product.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 42.0,
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
        self.assertEqual(purchase_order.picking_count, 1)
        # Create Work Acceptance
        work_acceptance = self.env["work.acceptance"].create(
            {
                "purchase_id": purchase_order.id,
                "partner_id": self.res_partner.id,
                "responsible_id": self.employee.id,
                "date_due": self.date_now,
                "date_receive": self.date_now,
                "company_id": self.env.ref("base.main_company").id,
                "wa_line_ids": [
                    (
                        0,
                        0,
                        {
                            "purchase_line_id": purchase_order.order_line[0].id,
                            "product_id": purchase_order.order_line[0].product_id.id,
                            "name": purchase_order.order_line[0].name,
                            "price_unit": purchase_order.order_line[0].price_unit,
                            "product_uom": purchase_order.order_line[0].product_uom.id,
                            "product_qty": 42.0,
                        },
                    )
                ],
            }
        )
        work_acceptance.button_accept()
        self.assertEqual(work_acceptance.state, "accept")
        self.assertEqual(purchase_order.wa_count, 1)
        # Received Products
        picking = purchase_order.picking_ids[0]
        self.assertEqual(len(picking.move_ids_without_package), 1)
        picking.wa_id = work_acceptance
        picking._onchange_wa_id()

        with self.assertRaises(ValidationError):
            picking.move_ids_without_package[0].quantity_done = 30.0
            picking.button_validate()
        picking.move_ids_without_package[0].quantity_done = 42.0
        picking.button_validate()
        # Create Vendor Bill
        f = Form(self.env["account.move"].with_context(default_type="in_invoice"))
        f.partner_id = purchase_order.partner_id
        f.purchase_id = purchase_order
        # f.wa_id = work_acceptance
        invoice = f.save()
        invoice.wa_id = work_acceptance
        invoice_line = invoice.invoice_line_ids[0]
        with self.assertRaises(ValidationError):
            invoice_line.with_context(check_move_validity=False).write(
                {"quantity": 6.0}
            )
            invoice.action_post()  # Warn when quantity not equal to WA
        invoice_line.quantity = 42.0
        invoice.action_post()

    def test_03_flow_service(self):
        # Create Purchase Order
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.res_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_product.id,
                            "product_uom": self.service_product.uom_id.id,
                            "name": self.service_product.name,
                            "price_unit": self.service_product.standard_price,
                            "date_planned": self.date_now,
                            "product_qty": 30.0,
                        },
                    )
                ],
            }
        )
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
        # Create Work Acceptance
        work_acceptance = self.env["work.acceptance"].create(
            {
                "purchase_id": purchase_order.id,
                "partner_id": self.res_partner.id,
                "responsible_id": self.employee.id,
                "date_due": self.date_now,
                "date_receive": self.date_now,
                "company_id": self.env.ref("base.main_company").id,
                "wa_line_ids": [
                    (
                        0,
                        0,
                        {
                            "purchase_line_id": purchase_order.order_line[0].id,
                            "product_id": purchase_order.order_line[0].product_id.id,
                            "name": purchase_order.order_line[0].name,
                            "price_unit": purchase_order.order_line[0].price_unit,
                            "product_uom": purchase_order.order_line[0].product_uom.id,
                            "product_qty": 30.0,
                        },
                    )
                ],
            }
        )
        work_acceptance.button_accept()
        self.assertEqual(work_acceptance.state, "accept")
        self.assertEqual(purchase_order.wa_count, 1)
        # Create Vendor Bill
        purchase_order.with_context(create_bill=True).action_view_invoice()
        wizard = self.env["select.work.acceptance.wizard"].create(
            {"wa_id": work_acceptance.id}
        )
        wiz = wizard.button_create_vendor_bill()
        f = Form(self.env["account.move"].with_context(wiz.get("context", {})))
        f.purchase_id = purchase_order
        invoice = f.save()
        invoice._onchange_purchase_auto_complete()
        self.assertEqual(invoice.state, "draft")
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
