# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.fields import Datetime


class TestPurchaseOpenQty(TransactionCase):
    def setUp(self):
        super(TestPurchaseOpenQty, self).setUp()
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
        # Purchase Order Num 1
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
            'price_unit': 1.0,
            'product_qty': 5.0,
            'account_analytic_id': self.analytic_account_1.id,
        }
        self.purchase_order_line_1 = \
            purchase_order_line_model.sudo().create(pl_dict1)
        self.purchase_order_1.button_confirm()

    def test_compute_qty_to_invoice_and_receive(self):
        self.assertEqual(self.purchase_order_line_1.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO line")
        self.assertEqual(self.purchase_order_line_1.qty_to_receive, 5.0,
                         "Expected 5 as qty_to_receive in the PO line")
        self.assertEqual(self.purchase_order_1.qty_to_invoice, 5.0,
                         "Expected 5 as qty_to_invoice in the PO")
        self.assertEqual(self.purchase_order_1.qty_to_receive, 5.0,
                         "Expected 5 as qty_to_receive in the PO")

    def test_search_qty_to_invoice_and_receive(self):
        found = self.purchase_order_model.search(
            ['|', ('qty_to_invoice', '>', 0.0), ('qty_to_receive', '>', 0.0)])
        self.assertTrue(
            self.purchase_order_1.id in found.ids,
            'Expected PO %s in POs %s' % (self.purchase_order_1.id, found.ids))
