# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tests.common import TransactionCase


class TestPoAmountBlock(TransactionCase):

    def setUp(self):
        super(TestPoAmountBlock, self).setUp()
        self.users_obj = self.env['res.users']
        self.po_obj = self.env['purchase.order']
        self.po_block_obj = self.env['purchase.approval.block.reason']
        # company
        self.company1 = self.env.ref('base.main_company')
        # groups
        self.group_purchase_user = self.env.ref('purchase.group_purchase_user')
        self.group_purchase_manager = self.env.ref(
            'purchase.group_purchase_manager')
        # Partner
        self.partner1 = self.env.ref('base.res_partner_1')
        # Products
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')
        self.product3 = self.env.ref('product.product_product_11')
        # Create users
        self.user1_id = self._create_user(
            'user_1',
            [self.group_purchase_user],
            self.company1,
        )
        self.user2_id = self._create_user(
            'user_2',
            [self.group_purchase_manager],
            self.company1,
        )

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user =\
            self.users_obj.with_context({'no_reset_password': True}).\
            create({
                'name': 'Purchase User',
                'login': login,
                'password': 'test',
                'email': 'test@yourcompany.com',
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, group_ids)],
            })
        return user.id

    def _create_purchase(self, line_products):
        """ Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                'name': product.name,
                'product_id': product.id,
                'product_qty': qty,
                'product_uom': product.uom_id.id,
                'price_unit': 100,
                'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }
            lines.append((0, 0, line_values))
        purchase = self.po_obj.create({
            'partner_id': self.partner1.id,
            'approval_block_id': self.po_block_obj.id,
            'order_line': lines,
            'company_id': self.company1.id,
        })
        return purchase

    def test_po_amount_block_1(self):
        "Test PO Block for Minimum Threshold Vendor Amount"
        self.partner1.write({'minimum_po_amount': 1500.00})

        # Create a PO with an amount below the minimum and check that the
        # Approval Block Reason is correctly assign
        purchase1 = self._create_purchase(
            [(self.product1, 1),
             (self.product2, 5),
             (self.product3, 8),
             ]
        )

        self.assertEquals(
            purchase1.approval_block_id,
            self.env.ref(
                'purchase_minimum_amount.minimum_amount_block_reason'))

        # Release the PO by pressing the button and then confirming the order
        purchase1.sudo(self.user2_id).button_release_approval_block()
        purchase1.sudo(self.user1_id).button_confirm()
        self.assertEquals(purchase1.state, 'purchase')

    def test_po_amount_block_2(self):
        "Test PO Block for Minimum Threshold Vendor Amount"
        self.partner1.write({'minimum_po_amount': 1500.00})

        purchase1 = self._create_purchase(
            [(self.product1, 1),
             (self.product2, 5),
             (self.product3, 8)])

        self.assertEquals(
            purchase1.approval_block_id,
            self.env.ref(
                'purchase_minimum_amount.minimum_amount_block_reason'))

        for po_line in purchase1.order_line:
            if po_line.product_id == self.product1:
                po_line.product_qty = 10

        self.assertEquals(
            purchase1.approval_block_id,
            self.env['purchase.approval.block.reason'])

        purchase1.sudo(self.user1_id).button_confirm()
        self.assertEquals(purchase1.state, 'purchase')
