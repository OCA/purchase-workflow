# Copyright 2017-2020 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestPurchaseRequest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pr_model = cls.env["purchase.request"]
        cls.prl_model = cls.env["purchase.request.line"]
        cls.usr_model = cls.env["res.users"]
        cls.dep_model = cls.env["hr.department"]
        cls.empee_model = cls.env["hr.employee"]
        dept_dict = {"name": "testing department"}
        cls.department_test = cls.dep_model.create(dept_dict)
        user_dict = {
            "name": "User test",
            "login": "tua@example.com",
            "password": "base-test-passwd",
            "email": "armande.hruser@example.com",
            "group_ids": [
                (4, cls.env.ref("purchase_request.group_purchase_request_user").id)
            ],
        }
        cls.user_test = cls.usr_model.create(user_dict)
        employee_dict = {
            "name": "Employee test",
            "department_id": cls.department_test.id,
            "user_id": cls.user_test.id,
        }
        cls.emp_test = cls.empee_model.create(employee_dict)
        dept_dict2 = {"name": "testing department"}
        cls.department_test2 = cls.dep_model.create(dept_dict2)
        user_dict2 = {
            "name": "User test",
            "login": "tua@example2.com",
            "password": "base-test-passwd",
            "email": "armande.hruser@example.com",
            "group_ids": [
                (4, cls.env.ref("purchase_request.group_purchase_request_user").id)
            ],
        }
        cls.user_test2 = cls.usr_model.create(user_dict2)
        employee_dict2 = {
            "name": "Employee test",
            "department_id": cls.department_test2.id,
            "user_id": cls.user_test2.id,
        }
        cls.emp_test2 = cls.empee_model.create(employee_dict2)
        pr_dict = {
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "requested_by": cls.user_test.id,
        }
        cls.purchase_request = cls.pr_model.with_user(cls.user_test).create(pr_dict)

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "is_storable": True,
            }
        )

        prl_test = {
            "request_id": cls.purchase_request.id,
            "product_id": cls.product.id,
            "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        cls.purchase_request_line = cls.prl_model.create(prl_test)
        cls.purchase_request.button_to_approve()

    def test_purchase_request_department(self):
        self.assertEqual(
            self.purchase_request.department_id,
            self.department_test,
            "Invalid department found in the purchase request",
        )

    def test_purchase_request_line_department(self):
        self.assertEqual(
            self.purchase_request_line.department_id,
            self.department_test,
            "Invalid department found in the purchase request line",
        )

    def test_onchange_method(self):
        self.purchase_request.button_draft()
        self.purchase_request.sudo().requested_by = self.user_test2
        self.purchase_request.sudo().onchange_requested_by()
        self.assertEqual(
            self.purchase_request.department_id,
            self.department_test2,
            "Invalid department found in the purchase request",
        )
