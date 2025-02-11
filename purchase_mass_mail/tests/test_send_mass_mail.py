# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSendSomePurchaseOrders(TransactionCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.partner = self.env["res.partner"].create({"name": "Test1"})
        self.product1 = self.env["product.product"].create(
            {
                "name": "Product A",
                "default_code": "PA",
                "lst_price": 100.0,
                "standard_price": 100.0,
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Product B",
                "default_code": "PB",
                "lst_price": 50.0,
                "standard_price": 50.0,
            }
        )
        self.po1 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": self.product1.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 12,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )
        self.po2 = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product2.id,
                            "name": self.product2.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 12,
                            "product_uom": self.product2.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )

    def test_send_mass_email_pos(self):
        pos = self.po1 + self.po2
        template = self.env.ref("purchase.email_template_edi_purchase", False)
        ctx = dict(
            self.env.context,
            default_model="purchase.order",
            default_use_template=True,
            active_model="purchase.order",
            active_id=self.po1.id,
            active_ids=pos.ids,
            partner_ids=self.partner,
            default_template_id=template and template.id,
            default_composition_mode="mass_mail",
            mark_rfq_as_sent=True,
        )
        self.po1.action_all_rfq_related_send()
        wizard_f = Form(self.env["mail.compose.message"].with_context(**ctx))
        wizard_f.save().action_send_mail()
        self.assertEqual(self.po1.state, "sent")
        self.assertEqual(self.po2.state, "sent")
        message = self.po1.message_ids[0]
        self.assertTrue(message.body)
        self.assertTrue(message.subject)
