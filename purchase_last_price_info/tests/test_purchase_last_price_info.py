# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from datetime import datetime
import openerp.tests.common as common


class TestPurchaseLastPriceInfo(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseLastPriceInfo, self).setUp()
        self.purchase_line_model = self.env['purchase.order.line']
        self.product = self.env.ref('product.product_product_31')

    def test_purchase_last_price_info_demo(self):
        purchase_lines = self.purchase_line_model.search(
            [('product_id', '=', self.product.id),
             ('state', 'in', ['confirmed', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.assertEqual(
            datetime.strptime(
                purchase_lines[:1].order_id.date_order,
                "%Y-%m-%d %H:%M:%S").date(),
            datetime.strptime(self.product.last_purchase_date,
                              "%Y-%m-%d").date())
        self.assertEqual(
            purchase_lines[:1].price_unit, self.product.last_purchase_price)
        self.assertEqual(
            purchase_lines[:1].order_id.partner_id,
            self.product.last_supplier_id)
