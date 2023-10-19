# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseAnalyticTag(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})
        cls.plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Projects Plan",
                "company_id": False,
            }
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {
                "name": "Test account 1",
                "plan_id": cls.plan.id,
            },
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {
                "name": "Test account 2",
                "plan_id": cls.plan.id,
            },
        )
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})
        cls.order = cls.create_purchase_order(cls)

    def create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.vendor
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        return order_form.save()

    def _action_confirm_create_invoice(self):
        self.order.button_confirm()
        self.order.order_line.qty_received = self.order.order_line.product_qty
        res = self.order.action_create_invoice()
        return self.env[res["res_model"]].browse(res["res_id"])

    def test_purchase_without_tags(self):
        self.order.order_line.analytic_distribution = {self.analytic_account_1.id: 100}
        invoice = self._action_confirm_create_invoice()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_purchase_with_tag_01(self):
        self.order.order_line.analytic_distribution = {self.analytic_account_1.id: 100}
        self.order.order_line.analytic_tag_ids = self.analytic_tag_1
        invoice = self._action_confirm_create_invoice()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_purchase_with_tag_02(self):
        self.order.order_line.analytic_distribution = {self.analytic_account_1.id: 100}
        self.order.order_line.analytic_tag_ids = self.analytic_tag_2
        invoice = self._action_confirm_create_invoice()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    def test_purchase_with_tags(self):
        self.order.order_line.analytic_distribution = {self.analytic_account_1.id: 100}
        self.order.order_line.analytic_tag_ids = (
            self.analytic_tag_1 + self.analytic_tag_2
        )
        invoice = self._action_confirm_create_invoice()
        tags = invoice.mapped("invoice_line_ids.analytic_tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)
