# -*- coding: utf-8 -*-
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
        dept_dict = {
            'name': 'testing department'
        }
        self.department_test = self.dep_model.create(dept_dict)
        user_dict = {
            'name': 'User test',
            'login': 'tua@example.com',
            'password': 'base-test-passwd',
            'email': 'armande.hruser@example.com',
            'groups_id': [(4, self.env.ref(
                'purchase_request.group_purchase_request_user').id)]
        }
        user_test = self.usr_model.create(user_dict)
        employee_dict = {
            'name': 'Employee test',
            'department_id': self.department_test.id,
            'user_id': user_test.id
        }
        self.emp_test = self.empee_model.create(employee_dict)
        dept_dict2 = {
            'name': 'testing department'
        }
        self.department_test2 = self.dep_model.create(dept_dict2)
        user_dict2 = {
            'name': 'User test',
            'login': 'tua@example2.com',
            'password': 'base-test-passwd',
            'email': 'armande.hruser@example.com',
            'groups_id': [(4, self.env.ref(
                'purchase_request.group_purchase_request_user').id)]
        }
        self.user_test2 = self.usr_model.create(user_dict2)
        employee_dict2 = {
            'name': 'Employee test',
            'department_id': self.department_test2.id,
            'user_id': self.user_test2.id
        }
        self.emp_test2 = self.empee_model.create(employee_dict2)
        pr_dict = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': user_test.id,
        }
        self.purchase_request = self.pr_model.sudo(user_test).create(pr_dict)
        prl_test = {
            'request_id': self.purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        self.purchase_request_line = self.prl_model.create(prl_test)
        self.purchase_request.button_to_approve()

    def test_purchase_request_department(self):

        self.assertEqual(self.purchase_request.department_id,
                         self.department_test, 'Invalid department found in '
                                               'the purchase request')

    def test_purchase_request_line_department(self):
        self.assertEqual(self.purchase_request_line.department_id,
                         self.department_test, 'Invalid department found in '
                                               'the purchase request line')

    def test_onchange_method(self):
        self.purchase_request.button_draft()
        self.purchase_request.sudo().requested_by = self.user_test2
        self.purchase_request.sudo().onchange_requested_by()
        self.assertEqual(self.purchase_request.department_id,
                         self.department_test2, 'Invalid department found in '
                                                'the purchase request')
