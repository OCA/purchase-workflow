# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp import fields


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.product_1 = self.env.ref('product.product_product_4')
        self.product_2 = self.env.ref('product.product_product_5b')
        po_model = self.env['purchase.order.line']
        self.purchase_order = self.env['purchase.order'].create(
            {'partner_id': self.env.ref('base.res_partner_3').id})
        self.po_line_1 = po_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product_1.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1.0,
             'product_uom': self.product_1.uom_id.id,
             'discount': 50.0,
             'price_unit': 10.0})
        self.tax = self.env['account.tax'].create(
            {'name': 'Sample tax 15%',
             'amount_type': 'percent',
             'type_tax_use': 'purchase',
             'amount': 15.0})
        self.po_line_2 = po_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product_2.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 10.0,
             'product_uom': self.product_2.uom_id.id,
             'discount': 30,
             'taxes_id': [(6, 0, [self.tax.id])],
             'price_unit': 230.0})

    def test_purchase_order_vals(self):
        self.assertEqual(self.po_line_1.price_subtotal, 5.0)
        self.assertEqual(self.po_line_2.price_subtotal, 1610.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1615.0)
        self.assertEqual(self.purchase_order.amount_tax, 241.5)
