# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
# Copyright 2018 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase
from odoo.fields import Datetime


class TestAnalyticSearch(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAnalyticSearch, cls).setUpClass()
        cls.purchase_order_model = cls.env['purchase.order']
        partner_model = cls.env['res.partner']
        prod_model = cls.env['product.product']
        analytic_account_model = cls.env['account.analytic.account']
        cls.product_uom_model = cls.env['product.uom']

        pa_dict = {
            'name': 'Partner 1',
            'supplier': True,
        }
        cls.partner = partner_model.create(pa_dict)
        uom_id = cls.product_uom_model.search([
            ('name', '=', 'Unit(s)')])[0].id
        pr_dict = {
            'name': 'Product Test',
            'uom_id': uom_id,
        }
        cls.product = prod_model.create(pr_dict)
        ac_dict = {
            'name': 'account 1',
        }
        cls.analytic_account_1 = \
            analytic_account_model.create(ac_dict)
        ac_dict = {
            'name': 'dummyname',
        }
        cls.analytic_account_2 = \
            analytic_account_model.create(ac_dict)
        # PURCHASE ORDER NUM 1 => account 1
        po_dict = {
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_1.id,
                    }),
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_1.id,
                    })],
        }
        cls.purchase_order_1 = cls.purchase_order_model.create(po_dict)

        # PURCHASE ORDER NUM 2 => account 1 and 2
        pa_dict2 = {
            'name': 'Partner 2',
            'supplier': True,
        }
        cls.partner2 = partner_model.create(pa_dict2)
        po_dict2 = {
            'partner_id': cls.partner2.id,
            'order_line': [
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_1.id,
                }),
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_2.id,
                }),
            ]
        }
        cls.purchase_order_2 = cls.purchase_order_model.create(po_dict2)
        # PURCHASE ORDER NUM 3 => account 2
        po_dict3 = {
            'partner_id': cls.partner2.id,
            'order_line': [
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_2.id,
                }),
                (0, 0, {
                    'date_planned': Datetime.now(),
                    'name': 'PO01',
                    'product_id': cls.product.id,
                    'product_uom': uom_id,
                    'price_unit': 1,
                    'product_qty': 5.0,
                    'account_analytic_id': cls.analytic_account_2.id,
                }),
            ]
        }

        cls.purchase_order_3 = cls.purchase_order_model.create(po_dict3)

    def test_filter_analytic_accounts(self):
        found = self.purchase_order_model.search([
            ('account_analytic_ids', '=', self.analytic_account_1.id)])
        self.assertEqual(
            found,
            self.purchase_order_1 + self.purchase_order_2
        )

    def test_filter_analytic_accounts_by_name(self):
        found = self.purchase_order_model.search([
            ('account_analytic_ids', '=', 'nt 1')])
        self.assertEqual(
            found,
            self.purchase_order_1 + self.purchase_order_2
        )

    def test_filter_analytic_accounts_not_equal(self):
        found = self.purchase_order_model.search([
            ('account_analytic_ids', '!=', self.analytic_account_1.id)])
        self.assertTrue(
            self.purchase_order_3 in found
        )
        self.assertTrue(
            self.purchase_order_1 not in found
        )
        self.assertTrue(
            self.purchase_order_2 not in found
        )

    def test_compute_analytic_accounts(self):
        self.assertEqual(self.purchase_order_1.account_analytic_ids,
                         self.analytic_account_1)
        self.assertEqual(self.purchase_order_2.account_analytic_ids,
                         self.analytic_account_1 + self.analytic_account_2)
