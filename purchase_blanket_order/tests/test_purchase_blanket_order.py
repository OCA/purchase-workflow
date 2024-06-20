# Copyright (C) 2018 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestPurchaseBlanketOrders(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.blanket_order_obj = self.env["purchase.blanket.order"]
        self.blanket_order_line_obj = self.env["purchase.blanket.order.line"]
        self.blanket_order_wiz_obj = self.env["purchase.blanket.order.wizard"]

        self.partner = self.env["res.partner"].create(
            {"name": "TEST SUPPLIER", "supplier_rank": 1}
        )
        self.payment_term = self.env.ref("account.account_payment_term_30days")

        # Seller IDS
        seller = self.env["product.supplierinfo"].create(
            {"name": self.partner.id, "price": 30.0}
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Demo",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 35.0,
                "seller_ids": [(6, 0, [seller.id])],
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL01",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Demo 2",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 50.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL02",
            }
        )

        self.yesterday = date.today() - timedelta(days=1)
        self.tomorrow = date.today() + timedelta(days=1)

    def _get_po_from_wizard(self, res):
        return self.env[res["res_model"]].search(res["domain"])

    def test_01_create_blanket_order_flow(self):
        """ We create a blanket order and check constrains to confirm BO """
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.yesterday),
                "payment_term_id": self.payment_term.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 0.0,  # will be updated later
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.line_ids[0].sudo().onchange_product()
        blanket_order._compute_line_count()
        blanket_order._compute_uom_qty()

        self.assertEqual(blanket_order.state, "draft")
        self.assertEqual(blanket_order.line_ids[0].price_unit, 30.0)
        self.assertEqual(blanket_order.original_uom_qty, 20.0)
        self.assertEqual(blanket_order.ordered_uom_qty, 0.0)
        self.assertEqual(blanket_order.remaining_uom_qty, 20.0)

        # date in the past
        self.assertEqual(blanket_order.state, "draft")
        with self.assertRaises(UserError):
            blanket_order.sudo().action_confirm()

        blanket_order.validity_date = fields.Date.to_string(self.tomorrow)
        blanket_order.name = "Draft"
        blanket_order.sudo().action_confirm()
        self.assertNotEqual(blanket_order.name, "Draft")

        blanket_order.validity_date = fields.Date.to_string(self.yesterday)
        self.assertEqual(blanket_order.state, "expired")
        blanket_order.validity_date = fields.Date.to_string(self.tomorrow)

        blanket_order.sudo().action_cancel()
        self.assertEqual(blanket_order.state, "expired")
        blanket_order.sudo().set_to_draft()
        self.assertEqual(blanket_order.state, "draft")
        action = blanket_order.action_pbo_send()
        mail_form = Form(
            self.env["mail.compose.message"].with_context(action["context"])
        )
        mail = mail_form.save()
        mail.send_mail()
        self.assertEqual(blanket_order.state, "sent")
        previous_name = blanket_order.name
        blanket_order.sudo().action_confirm()
        self.assertEqual(previous_name, blanket_order.name)

        self.assertEqual(blanket_order.state, "open")
        blanket_order.action_view_purchase_blanket_order_line()

        # Search view check
        blanket_order._search_original_uom_qty(">=", 0.0)
        blanket_order._search_ordered_uom_qty(">=", 0.0)
        blanket_order._search_invoiced_uom_qty(">=", 0.0)
        blanket_order._search_received_uom_qty(">=", 0.0)
        blanket_order._search_remaining_uom_qty(">=", 0.0)
        with self.assertRaises(UserError):
            blanket_order.unlink()

    def test__02_create_purchase_orders_from_blanket_order(self):
        """ We create a blanket order and create two purchase orders """
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "partner_ref": "REF",
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 30.0,
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()

        with self.assertRaises(UserError):
            # Blanket order is not confirmed
            self.blanket_order_wiz_obj.with_context(
                active_id=blanket_order.id, active_model="purchase.blanket.order"
            ).create({})
        blanket_order.sudo().action_confirm()

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="purchase.blanket.order"
        ).create({})
        wizard1.line_ids[0].write({"qty": 30.0})

        with self.assertRaises(UserError):
            # Wizard quantity greater than remaining quantity
            wizard1.sudo().create_purchase_order()
        wizard1.line_ids[0].write({"qty": 10.0})
        res = wizard1.sudo().create_purchase_order()
        po = self._get_po_from_wizard(res)
        self.assertEqual(po.partner_ref, "REF")

        wizard2 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id, active_model="purchase.blanket.order"
        ).create({})
        wizard2.line_ids[0].write({"qty": 10.0})
        res = wizard2.sudo().create_purchase_order()
        po = self._get_po_from_wizard(res)
        self.assertEqual(po.partner_ref, "REF")

        with self.assertRaises(UserError):
            # Blanket order already completed
            self.blanket_order_wiz_obj.with_context(
                active_id=blanket_order.id, active_model="purchase.blanket.order"
            ).create({})

        self.assertEqual(blanket_order.state, "done")

        self.assertEqual(blanket_order.purchase_count, 2)

        view_action = blanket_order.action_view_purchase_orders()
        domain_ids = view_action["domain"][0][2]
        self.assertEqual(len(domain_ids), 2)

    def test_03_create_purchase_orders_from_blanket_order_line(self):
        """ We create a blanket order and create two purchase orders
            from the blanket order lines """
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "partner_ref": "REF",
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 30.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "original_uom_qty": 50.0,
                            "price_unit": 60.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.sudo().action_confirm()

        bo_lines = self.blanket_order_line_obj.search([])
        self.assertEqual(len(bo_lines), 2)

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_ids=[bo_lines[0].id, bo_lines[1].id]
        ).create({})
        self.assertEqual(len(wizard1.line_ids), 2)
        wizard1.line_ids[0].write({"qty": 10.0})
        wizard1.line_ids[1].write({"qty": 20.0})
        wizard1.sudo().create_purchase_order()

        self.assertEqual(bo_lines[0].remaining_uom_qty, 10.0)
        self.assertEqual(bo_lines[1].remaining_uom_qty, 30.0)

    def test_04_purchase_blanket_order_sequence(self):
        """ We create a blanket order and the name created by sequence """
        company = self.env.user.company_id
        self.env["ir.sequence"].search([("code", "=", "purchase.blanket.order")]).write(
            {"prefix": "PBO/TEST/"}
        )
        vals = {
            "partner_id": self.partner.id,
            "partner_ref": "REF",
            "validity_date": fields.Date.to_string(self.tomorrow),
            "payment_term_id": self.payment_term.id,
            "company_id": company.id,
        }
        blanket_order = self.blanket_order_obj.create(vals.copy())
        self.assertTrue(blanket_order.name.startswith("PBO/TEST/"))

    def test_05_create_blanket_order_without_template_and_compose(self):
        """ We create a blanket order and check constrains to send by mail """
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 20.0,
                            "price_unit": 0.0,  # will be updated later
                        },
                    )
                ],
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.line_ids[0].sudo().onchange_product()
        blanket_order._compute_line_count()
        blanket_order._compute_uom_qty()

        # Unlink the mail template to test the case that the action
        # doesn't have a default template id
        self.env.ref(
            "purchase_blanket_order.email_template_edi_purchase_blanket_order"
        ).unlink()
        view = self.env.ref("mail.email_compose_message_wizard_form")

        # Unlink the mail form to test the case that the action doesn't have a view id
        self.env["ir.ui.view"].search([("inherit_id", "=", view.id)]).unlink()
        view.unlink()
        action = blanket_order.action_pbo_send()
        self.assertFalse(action["view_id"])
        self.assertFalse(action["context"]["default_template_id"])
