# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)

import odoo.tests.common as common
from odoo import fields


class TestPurchaseLastPriceInfo(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseLastPriceInfo, self).setUp()
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.product = self.env.ref('product.consu_delivery_01')
        self.partner = self.env.ref('base.res_partner_1')

    def test_purchase_last_price_info_demo(self):
        purchase_order = self.env.ref('purchase.purchase_order_6')
        purchase_order.button_confirm()
        purchase_lines = self.purchase_line_model.search(
            [('product_id', '=', self.product.id),
             ('state', 'in', ['purchase', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.assertEqual(
            fields.Datetime.from_string(
                purchase_lines[:1].order_id.date_order).date(),
            fields.Datetime.from_string(
                self.product.last_purchase_date).date())
        self.assertEqual(
            purchase_lines[:1].price_unit, self.product.last_purchase_price)
        self.assertEqual(
            purchase_lines[:1].order_id.partner_id,
            self.product.last_supplier_id)

    def _create_purchase(self, products, price=None):
        purchase_order_form = common.Form(self.purchase_model)
        purchase_order_form.partner_id = self.partner
        for product in products:
            with purchase_order_form.order_line.new() as line:
                line.product_id = product
                if price is not None:
                    line.price_unit = price
        purchase_order = purchase_order_form.save()
        purchase_order.button_confirm()
        return purchase_order

    def test_purchase_last_price_info_new_order(self):
        purchase_order = self._create_purchase(self.product)
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
