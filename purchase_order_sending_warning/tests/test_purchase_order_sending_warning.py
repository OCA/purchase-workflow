from odoo import fields
from odoo.tests.common import Form

from odoo.addons.test_mail.tests.common import TestMailCommon


class TestPurchaseOrderSendingWarning(TestMailCommon):
    def setUp(self):
        super(TestPurchaseOrderSendingWarning, self).setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Supplier 1",
                "email": "example@yourcompany.com",
                "phone": 123456789,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Product1",
            }
        )
        self.seller = self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_code": "12345",
                "price": 99.0,
            }
        )
        self.purchase_model = self.env["purchase.order"]

    def test_purchase_order_warning_send(self):
        self.purchase_order = self.purchase_model.create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.standard_price,
                            "name": self.product.name,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 1,
                        },
                    )
                ],
            }
        )

        template = self.env.ref("purchase.email_template_edi_purchase", False)

        ctx = dict(
            self.env.context,
            default_model="purchase.order",
            default_use_template=True,
            active_model="purchase.order",
            active_id=self.purchase_order.id,
            active_ids=self.purchase_order.ids,
            partner_ids=self.supplier.id,
            default_template_id=template and template.id,
            mark_rfq_as_sent=True,
        )
        self.purchase_order.action_rfq_send()
        wizard_f = Form(self.env["mail.compose.message"].with_context(ctx))

        with self.mock_mail_gateway(sim_error="connect_smtp_notfound"):
            wizard_f.save().send_mail()
            self.assertEqual(self.purchase_order.sending_error_type, "email_not_sent")
            self.assertTrue(self.purchase_order.transmission_error)
