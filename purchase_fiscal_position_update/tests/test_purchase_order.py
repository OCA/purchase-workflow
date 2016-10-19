# -*- coding: utf-8 -*-
# Copyright 2016 - Tecnativa - Angel Moya <odoo@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase

import time


class TestAccountInvoice(TransactionCase):

    def setUp(self):
        super(TestAccountInvoice, self).setUp()

        self.fiscal_position_model = self.env['account.fiscal.position']
        self.tax_model = self.env['account.tax']
        self.product_model = self.env['product.product']
        self.purchase_order_model = self.env['purchase.order']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.partner = self.browse_ref("base.res_partner_2")
        self.account_model = self.env['account.account']
        account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        self.account_rcv = self.account_model.create({
            'code': "cust_acc",
            'name': "customer account",
            'user_type_id': account_user_type.id,
            'reconcile': True,
        })
        self.test_tax = self.tax_model.create({
            'name': "Test tax",
            'amount_type': 'fixed',
            'amount': 10,
            'sequence': 1,
        })
        self.test_tax_bis = self.tax_model.create({
            'name': "Test tax bis",
            'amount_type': 'fixed',
            'amount': 15,
            'sequence': 2,
        })
        self.product = self.product_model.create({
            'name': "Voiture",
            'list_price': '121',
            'supplier_taxes_id': [(6, 0, [self.test_tax.id])],
            'standard_price': 10
        })
        tax_vals = {
            'tax_src_id': self.test_tax.id,
            'tax_dest_id': self.test_tax_bis.id
        }
        self.fiscal_position = self.fiscal_position_model.create({
            'name': 'Test Fiscal Position',
            'tax_ids': [(0, 0, tax_vals)]
        })

        date_planned = time.strftime('%Y') + '-07-01'
        self.purchase = self.purchase_order_model.create({
            'partner_id': self.partner.id,
            'fiscal_position_id': False,
            'name': 'Test'
        })
        self.account_revenue = self.env['account.account'].search(
            [('user_type_id',
              '=',
              self.env.ref('account.data_account_type_revenue').id)],
            limit=1)
        self.purchase_line = self.purchase_order_line_model.create({
            'order_id': self.purchase.id,
            'product_qty': 3,
            'price_unit': 100,
            'name': 'Test Line',
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'date_planned': date_planned
        })
        self.product.supplier_taxes_id = self.test_tax
        self.purchase_line.onchange_product_id()

    def test_update_fiscal_position(self):
        self.assertEquals(
            self.purchase_line.taxes_id.id,
            self.test_tax.id
        )
        self.purchase.fiscal_position_id = self.fiscal_position
        self.purchase.onchange_fiscal_position_id()
        self.assertEquals(
            self.purchase_line.taxes_id.id,
            self.test_tax_bis.id
        )
