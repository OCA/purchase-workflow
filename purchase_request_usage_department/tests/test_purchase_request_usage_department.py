# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestPurchaseRequest(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequest, self).setUp()
        self.pr_model = self.env['purchase.request']
        self.prl_model = self.env['purchase.request.line']
        self.usr_model = self.env['res.users']
        self.dep_model = self.env['hr.department']
        self.empee_model = self.env['hr.employee']
        self.usage_model = self.env['purchase.product.usage']
        self.usage = self.usage_model.create({
            'name': 'Personal',
            'code': 'Ps',
        })
        self.usage_2 = self.usage_model.create({
            'name': 'Marketing',
            'code': 'Mk',
        })
        dept_dict = {
            'name': 'department in usage',
            'usage_id': self.usage.id
        }
        self.department_usage = self.dep_model.create(dept_dict)
        dept_dict = {
            'name': 'department with no usage',
            'usage_id': self.usage_2.id
        }
        self.department_usage_2 = self.dep_model.create(dept_dict)
        user_dict = {
            'name': 'User test',
            'login': 'u@example.com',
            'email': 'u@example.com',
            'groups_id': [(4, self.ref(
                'purchase_request.group_purchase_request_user'))]
        }
        self.user_dep_usage = self.usr_model.create(user_dict)
        employee_dict = {
            'name': 'Employee test',
            'department_id': self.department_usage.id,
            'user_id': self.user_dep_usage.id
        }
        self.emp_usage = self.empee_model.create(employee_dict)
        user_dict = {
            'name': 'User test 2',
            'login': 'u2@example.com',
            'email': 'u2@example.com',
            'groups_id': [(4, self.env.ref(
                'purchase_request.group_purchase_request_user').id)]
        }
        self.user_2 = self.usr_model.create(user_dict)
        employee_dict = {
            'name': 'Employee test 2',
            'user_id': self.user_2.id,
            'department_id': self.department_usage_2.id
        }
        self.emp_no_usage = self.empee_model.create(employee_dict)
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id
        })
        pr_dict = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': self.user_dep_usage.id,
        }
        self.purchase_request = self.pr_model.sudo(
            self.user_dep_usage).create(pr_dict)
        self.prl_test = {
            'request_id': self.purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_qty': 5.0,
        }
        self.purchase_request_line = self.prl_model.sudo(
            self.user_dep_usage).create(self.prl_test)
        user_dict = {
            'name': 'Orphan user',
            'login': 'ou@example.com',
            'email': 'ou@example.com',
            'groups_id': [(4, self.env.ref(
                'purchase_request.group_purchase_request_user').id)]
        }
        self.user_orphan = self.usr_model.create(user_dict)

    def test_purchase_request_department_usage(self):
        self.assertEqual(
            self.purchase_request_line.department_id.usage_id,
            self.usage, 'Invalid usage found in the purchase request')
        self.assertEqual(
            self.purchase_request_line.request_id.department_id,
            self.department_usage,
            'Invalid department found in the purchase request')

    def test_onchange_method(self):
        self.purchase_request.sudo().requested_by = self.user_2
        self.purchase_request.sudo().onchange_requested_by()
        self.assertEqual(
            self.purchase_request_line.request_id.department_id,
            self.department_usage_2,
            'Invalid department found in the purchase request')
        self.purchase_request.sudo().onchange_department_id()
        self.assertEqual(
            self.purchase_request_line.usage_id, self.usage_2,
            'Invalid usage found in the purchase request')

    def test_purchase_request_orphan_department(self):
        self.purchase_request.sudo().requested_by = self.user_orphan
        self.purchase_request.sudo().onchange_requested_by()
        self.purchase_request.sudo().onchange_department_id()
        self.assertEqual(
            self.purchase_request_line.usage_id, self.usage_model,
            'Usage found in the purchase request')
