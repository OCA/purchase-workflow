# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests.common as common
from odoo import fields


class TestPurchaseLastPriceInfo(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseLastPriceInfo, self).setUp()
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.product = self.env.ref('product.service_order_01')
        self.partner = self.env.ref('base.res_partner_1')
        self.location = self.env.ref('stock.stock_location_suppliers')
        self.product_uom = self.env.ref('product.product_uom_hour')

    def test_purchase_last_price_info_demo(self):
        purchase_lines = self.purchase_line_model.search(
            [('product_id', '=', self.product.id),
             ('state', 'in', ['purchase', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.assertEqual(
            purchase_lines[:1].order_id.date_order,
            self.product.last_purchase_date)
        self.assertEqual(
            purchase_lines[:1].price_unit,
            self.product.last_purchase_price)
        self.assertEqual(
            purchase_lines[:1].order_id.partner_id,
            self.product.last_supplier_id)

    def test_purchase_last_price_info_new_order(self):
        purchase_order = self.purchase_model.create({
            'partner_id': self.partner.id,
            'location_id': self.location.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': self.product.standard_price,
                'product_qty': 1.0,
                'product_uom': self.product_uom.id,
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
