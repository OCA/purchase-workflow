from datetime import datetime

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderLineFilter(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date_planned = datetime.now()
        cls.purchase_user = cls.env["res.users"].with_context(no_reset_password=True)
        cls.department = (
            cls.env["hr.department"]
            .with_context(no_reset_password=True)
            .create({"name": "Test Department"})
        )
        cls.category = (
            cls.env["product.category"]
            .with_context(no_reset_password=True)
            .create({"name": "Test Category", "hr_department_id": cls.department.id})
        )
        cls.product = (
            cls.env["product.product"]
            .with_context(no_reset_password=True)
            .create({"name": "Test Product", "categ_id": cls.category.id})
        )
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "testuser@example.com",
                }
            )
        )
        cls.employee = (
            cls.env["hr.employee"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test Employee",
                    "department_id": cls.department.id,
                    "user_id": cls.user.id,
                }
            )
        )
        cls.partner_id = cls.env["res.partner"].create({"name": "Test vendor"})

    def test_purchase_order_line(self):
        purchase_order_form = Form(self.env["purchase.order"].with_user(self.user))
        purchase_order_form.partner_id = self.partner_id
        with purchase_order_form.order_line.new() as line:
            product_id = line.product_id.with_context(
                **{"purchase_order": True}
            ).search([])
            line.product_id = product_id

        po = purchase_order_form.save()
        self.assertEqual(
            po.order_line[0].product_id.categ_id.hr_department_id,
            self.user.employee_id.department_id,
        )

        purchase_order_form = Form(self.env["purchase.order"].with_user(self.user))
        purchase_order_form.partner_id = self.partner_id
        with purchase_order_form.order_line.new() as line:
            product_id = line.product_id.with_context(
                **{"purchase_order": True}
            ).name_search([])
            product_id = line.product_id.browse(product_id[0][0])
            line.product_id = product_id

        po = purchase_order_form.save()
        self.assertEqual(
            po.order_line[0].product_id.categ_id.hr_department_id,
            self.user.employee_id.department_id,
        )
