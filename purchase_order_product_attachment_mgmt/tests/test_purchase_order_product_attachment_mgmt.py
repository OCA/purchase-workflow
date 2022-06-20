# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.tests import Form, common


class TestPurchaseOrderProductAttachmentMgmt(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product_a = cls.env["product.product"].create({"name": "Test Product A"})
        cls.product_b = cls.env["product.product"].create({"name": "Test Product B"})
        cls.purchase_order = cls._create_purchase_order(cls)

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_a
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_b
        return order_form.save()

    def _create_attachment(self, product):
        return self.env["ir.attachment"].create(
            {
                "name": "Test file %s" % product.name,
                "res_model": product._name,
                "res_id": product.id,
                "datas": base64.b64encode(b"\xff data"),
            }
        )

    def test_purchase_order_documents(self):
        attachment_a = self._create_attachment(self.product_a)
        action = self.purchase_order.action_see_purchase_order_attachments()
        attachments = self.env["ir.attachment"].search(action["domain"])
        self.assertIn(attachment_a.id, attachments.ids)
        self.assertIn(self.product_a.id, attachments.mapped("res_id"))
        self.assertNotIn(self.product_b.id, attachments.mapped("res_id"))
        attachment_b = self._create_attachment(self.product_b)
        action = self.purchase_order.action_see_purchase_order_attachments()
        attachments = self.env["ir.attachment"].search(action["domain"])
        self.assertIn(attachment_b.id, attachments.ids)
        self.assertIn(self.product_a.id, attachments.mapped("res_id"))
        self.assertIn(self.product_b.id, attachments.mapped("res_id"))
