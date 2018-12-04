# -*- coding: utf-8 -*-

import odoo.tests.common as common
from odoo import fields


class TestPurchaseLastPriceInfo(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseLastPriceInfo, self).setUp()
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.product = self.env.ref('product.product_delivery_01')
        self.partner = self.env.ref('base.res_partner_1')
        self.product_uom = self.env.ref('product.product_uom_unit')

    def test_purchase_last_price_info_demo(self):
        purchase_line = self.purchase_line_model.search([
            ('product_id', '=', self.product.id),
            ('state', 'in', ['purchase', 'done'])
        ], order='date_order DESC', limit=1)
        self.assertEqual(
            fields.Date.from_string(
                purchase_line.date_order),
            fields.Date.from_string(
                self.product.last_purchase_date))
        self.assertEqual(
            purchase_line.price_unit, self.product.last_purchase_price)
        self.assertEqual(
            purchase_line.partner_id, self.product.last_supplier_id)

    def test_purchase_last_price_info_new_order(self):
        purchase_order = self.purchase_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': self.product.standard_price,
                'product_uom': self.product_uom.id,
                'product_qty': 1.0,
                'name': self.product.name,
                'date_planned': fields.Datetime.now(),
            })]
        })
        purchase_order.button_confirm()
        self.assertEqual(
            fields.Datetime.from_string(
                purchase_order.date_order).date(),
            fields.Datetime.from_string(
                self.product.last_purchase_date).date())
        self.assertEqual(
            purchase_order.order_line[:1].price_unit,
            self.product.last_purchase_price)
        self.assertEqual(
            self.partner, self.product.last_supplier_id)
