# -*- coding: utf-8 -*-
# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestPurchaseDeposit(TransactionCase):

    def setUp(self):
        super(TestPurchaseDeposit, self).setUp()
        self.product_model = self.env['product.product']
        self.account_model = self.env['account.account']
        self.invoice_model = self.env['account.invoice']
        self.partner = self.env.ref('base.res_partner_3')

        # Create Deposit Account
        self.account_deposit = self.account_model.create({
            'name': 'Purchase Deposit',
            'code': '11620',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
        })
        # Create products:
        p1 = self.product1 = self.product_model.create({
            'name': 'Test Product 1',
            'type': 'service',
            'default_code': 'PROD1',
            'purchase_method': 'purchase',
        })

        self.po = self.env['purchase.order'].create({
            'partner_id': self.ref('base.res_partner_3'),
            'order_line': [
                (0, 0, {'product_id': p1.id,
                        'product_uom': p1.uom_id.id,
                        'name': p1.name,
                        'price_unit': 100.0,
                        'date_planned': fields.Datetime.now(),
                        'product_qty': 42.0})]})

    def test_create_deposit_invoice(self):
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        CreateDeposit = self.env['purchase.advance.payment.inv']
        self.po.button_confirm()
        deposit = CreateDeposit.with_context(
            {'active_id': self.po.id, 'active_ids': [self.po.id]}).create(
            {'advance_payment_method': 'percentage', 'amount': 10.0,
             'deposit_account_id': self.account_deposit.id})
        deposit.create_invoices()
        # New Purchase Deposit is created automatically
        deposit_product_id = deposit.purchase_deposit_product_id
        # 1 Deposit Invoice is created
        self.assertEqual(self.po.invoice_ids.invoice_line_ids[0].product_id.id,
                         deposit_product_id.id)
        self.assertEqual(
            self.po.invoice_ids.invoice_line_ids[0].price_unit, 420.0)
        # On Purchase Order, there will be new deposit line create
        self.assertEqual(self.po.order_line[0].product_id.id,
                         self.product1.id)
        self.assertEqual(self.po.order_line[0].price_unit, 100.0)
        self.assertEqual(self.po.order_line[1].product_id.id,
                         deposit_product_id.id)
        self.assertEqual(self.po.order_line[1].price_unit, 420.0)
        # On Purchase Order, create normal billing
        self.po.with_context(create_bill=True).action_view_invoice()

        # Make invoice
        inv_1 = self.env['account.invoice'].with_context(
            type='in_invoice',
        ).create({
            'partner_id': self.partner.id,
            'purchase_id': self.po.id,
            'account_id': self.partner.property_account_payable_id.id
        })
        inv_1.purchase_order_change()
        self.assertEqual(
            inv_1.invoice_line_ids[0].product_id.id, self.product1.id)
        self.assertEqual(inv_1.invoice_line_ids[0].price_unit, 100.0)
        self.assertEqual(inv_1.invoice_line_ids[0].quantity, 42.0)
        self.assertEqual(inv_1.invoice_line_ids[1].product_id.id,
                         deposit_product_id.id)
        self.assertEqual(inv_1.invoice_line_ids[1].price_unit, 420.0)
        self.assertEqual(inv_1.invoice_line_ids[1].quantity, - 1)

    def test_create_deposit_invoice_exception(self):
        """This test focus on exception cases, when create deposit invoice,
        1. This action is allowed only in Purchase Order state
        2. The value of the deposit must be positive
        3. For type percentage, The percentage of the deposit must <= 100
        4. Purchase Deposit Product's purchase_method != purchase
        5. Purchase Deposit Product's type != service
        """
        self.assertEqual(len(self.po.order_line), 1)
        # We create invoice from expense
        CreateDeposit = self.env['purchase.advance.payment.inv']
        # 1. This action is allowed only in Purchase Order state
        with self.assertRaises(UserError):
            deposit = CreateDeposit.with_context(
                {'active_id': self.po.id}).create(
                {'advance_payment_method': 'fixed',
                 'deposit_account_id': self.account_deposit.id,
                 'amount': 10})
        self.po.button_confirm()
        self.assertEqual(self.po.state, 'purchase')
        # 2. The value of the deposit must be positive
        deposit = CreateDeposit.with_context(
            {'active_id': self.po.id,
             'active_ids': [self.po.id]}).create(
            {'advance_payment_method': 'fixed',
             'deposit_account_id': self.account_deposit.id,
             'amount': -10})
        with self.assertRaises(UserError):
            deposit.create_invoices()
        # 3. For type percentage, The percentage of the deposit must <= 100
        with self.assertRaises(UserError):
            deposit = CreateDeposit.with_context(
                {'active_id': self.po.id, 'active_ids': [self.po.id]}).create(
                {'advance_payment_method': 'percentage',
                 'deposit_account_id': self.account_deposit.id,
                 'amount': 101.0})
            deposit.create_invoices()
        deposit.amount = 10
        # 4. Purchase Deposit Product's purchase_method != purchase
        deposit_product_id = deposit.purchase_deposit_product_id
        deposit_product_id.write({'purchase_method': 'receive'})
        deposit.purchase_deposit_product_id = deposit_product_id
        with self.assertRaises(UserError):
            deposit.create_invoices()
        deposit_product_id.write({'purchase_method': 'purchase'})
        # 5. Purchase Deposit Product's type != service
        deposit_product_id.type = 'consu'
        with self.assertRaises(UserError):
            deposit.create_invoices()
