# -*- coding: utf-8 -*-
#
#
#    Authors: Alexandre Fayolle
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.tests import common

from .helper import AmendmentMixin

class TestResupplyAmendment(common.TransactionCase, AmendmentMixin):
    def setUp(self):
        super(TestResupplyAmendment, self).setUp()
        ref = self.env.ref
        self.amendment_model = self.env['purchase.order.amendment']
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.partner1 = ref('base.res_partner_2')
        self.product2 = ref('product.product_product_9')
        self.product3 = ref('product.product_product_11')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.purchase_pricelist = self.env.ref('purchase.list0')
        order_point = self.env['stock.warehouse.orderpoint']
        op_data = {'warehouse_id': ref('stock.warehouse0').id,
                   'location_id': ref('stock.stock_location_stock').id,
                   'product_min_qty': 80,
                   'product_max_qty': 123,
                   }
        self.order_points = order_point
        for product in (self.product2,
                        self.product3):
            product.route_ids = ref('purchase.route_warehouse0_buy')
            product.seller_ids[0].name = self.partner1
            op_data['product_id'] = product.id
            self.order_points |= order_point.create(op_data)
        self.env['procurement.order'].run_scheduler()
        self.purchase = self.order_points.mapped('procurement_ids.purchase_id')
        self.purchase.invoice_method = 'manual'
        self.purchase.signal_workflow('purchase_confirm')

    def test_po(self):
        self.assertEqual(len(self.purchase), 1)
        self.assert_moves([
            (self.product2, 101, 'assigned'),
            (self.product3, 97, 'assigned'),
        ])

    def test_ship_and_cancel_part(self):
        # We have 1000 product1
        # Ship 200 products
        self.assert_purchase_lines([
            (self.product2, 101, 'confirmed'),
            (self.product3, 97, 'confirmed'),
        ])
        self.ship([(self.product2, 51),
                   (self.product3, 0),
                   ])

        self.assert_moves([
            (self.product2, 51, 'done'),
            (self.product2, 50, 'assigned'),
            (self.product3, 97, 'assigned'),
        ])

        # amend the purchase order
        amendment = self.amend()

        # keep only 30 product2 of the 101 expected
        self.amend_product(amendment, self.product2, 30)
        self.assert_amendment_quantities(amendment,
                                         self.product2,
                                         ordered_qty=101,
                                         received_qty=51,
                                         amend_qty=30)
        self.assert_amendment_quantities(amendment,
                                         self.product3,
                                         ordered_qty=97,
                                         amend_qty=97)
        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product2, 20, 'cancel'),
            (self.product2, 51, 'confirmed'),
            (self.product2, 30, 'confirmed'),
            (self.product3, 97, 'confirmed'),
        ])
        self.assert_moves([
            (self.product2, 51, 'done'),
            (self.product2, 50, 'cancel'),
            (self.product2, 30, 'assigned'),
            (self.product3, 97, 'assigned'),
        ])
        self.assertEqual(self.purchase.state, 'approved')

