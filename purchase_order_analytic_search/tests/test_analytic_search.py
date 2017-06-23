# -*- coding: utf-8 -*-
# © 2015-17 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp.tests.common import TransactionCase
from openerp.fields import Datetime


class TestAnalyticSearch(TransactionCase):

    def setUp(self):
        super(TestAnalyticSearch, self).setUp()
        self.purchase_order_model = self.env['purchase.order']
        purchase_order_line_model = self.env['purchase.order.line']
        partner_model = self.env['res.partner']
        prod_model = self.env['product.product']
        analytic_account_model = self.env['account.analytic.account']
        self.product_uom_model = self.env['product.uom']

        pa_dict = {
            'name': 'Partner 1',
            'supplier': True,
        }
        self.partner = partner_model.sudo().create(pa_dict)
        po_dict = {
            'partner_id': self.partner.id,
        }
        # PURCHASE ORDER NUM 1
        self.purchase_order_1 = self.purchase_order_model.create(po_dict)
        uom_id = self.product_uom_model.search([
            ('name', '=', 'Unit(s)')])[0].id
        pr_dict = {
            'name': 'Product Test',
            'uom_id': uom_id,
        }
        self.product = prod_model.sudo().create(pr_dict)
        ac_dict = {
            'name': 'analytic account 1',
        }
        self.analytic_account_1 = \
            analytic_account_model.sudo().create(ac_dict)
        pl_dict1 = {
            'date_planned': Datetime.now(),
            'name': 'PO01',
            'order_id': self.purchase_order_1.id,
            'product_id': self.product.id,
            'product_uom': uom_id,
            'price_unit': 1,
            'product_qty': 5.0,
            'account_analytic_id': self.analytic_account_1.id,
        }
        self.purchase_order_line_1 = \
            purchase_order_line_model.sudo().create(pl_dict1)

        # PURCHASE ORDER NUM 2
        pa_dict2 = {
            'name': 'Partner 2',
            'supplier': True,
        }
        self.partner2 = partner_model.sudo().create(pa_dict2)
        po_dict2 = {
            'partner_id': self.partner2.id,
        }
        self.purchase_order_2 = self.purchase_order_model.create(po_dict2)

    def test_filter_analytic_accounts(self):
        found = self.purchase_order_model.search([
            ('account_analytic_ids', '=', self.analytic_account_1.id)])
        self.assertEqual(
            found, self.purchase_order_1,
            'Expected %s and got %s' % (self.purchase_order_1, found))

    def test_compute_analytic_accounts(self):
        self.assertDictContainsSubset(
            {self.purchase_order_1.id: [self.analytic_account_1.id]},
            self.purchase_order_1._compute_analytic_accounts(),
            'Method \'_compute_analytic_accounts\' does not work as expected.'
        )
