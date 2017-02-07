# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common
from openerp.exceptions import Warning as UserError
from openerp import fields


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.product_1 = self.env.ref('product.product_product_4')
        self.product_2 = self.env.ref('product.product_product_5b')
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.partner_3.fop_shipping = 250
        po_model = self.env['purchase.order.line']
        self.purchase_order1 = self.env['purchase.order'].create(
            {'partner_id': self.partner_3.id})
        self.po_line_1 = po_model.create(
            {'order_id': self.purchase_order1.id,
             'product_id': self.product_1.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1.0,
             'product_uom': self.product_1.uom_id.id,
             'price_unit': 100.0})
        self.purchase_order2 = self.env['purchase.order'].create(
            {'partner_id': self.partner_3.id})
        self.po_line_2 = po_model.create(
            {'order_id': self.purchase_order2.id,
             'product_id': self.product_2.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 10.0,
             'product_uom': self.product_2.uom_id.id,
             'price_unit': 45.0})

    def test_purchase_order_vals(self):
        with self.assertRaises(UserError):
            self.purchase_order1.button_approve()
        self.purchase_order2.button_approve()
        self.assertEqual(self.purchase_order1.state, 'draft')
        self.assertEqual(self.purchase_order2.state, 'purchase')
        self.purchase_order1.force_order_under_fop = True
        self.purchase_order1.button_approve()
        self.assertEqual(self.purchase_order1.state, 'purchase')
