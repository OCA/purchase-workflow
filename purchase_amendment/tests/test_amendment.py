# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
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


class TestAmendmentCombinations(common.TransactionCase, AmendmentMixin):

    def setUp(self):
        super(TestAmendmentCombinations, self).setUp()
        self.amendment_model = self.env['purchase.order.amendment']
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.partner1 = self.env.ref('base.res_partner_1')
        self.product1 = self.env.ref('product.product_product_7')
        self.product2 = self.env.ref('product.product_product_9')
        self.product3 = self.env.ref('product.product_product_11')
        self.location_stock = self.env.ref('stock.stock_location_stock')
        self.purchase_pricelist = self.env.ref('purchase.list0')
        self.purchase = self._create_purchase([(self.product1, 1000),
                                               (self.product2, 500),
                                               (self.product3, 800)])
        self.purchase.signal_workflow('purchase_confirm')

    def _create_purchase(self, line_products):
        """ Create a purchase order.

        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                'product_id': product.id,
                'product_qty': qty,
                'product_uom': product.uom_id.id,
                'price_unit': 50,
            }
            onchange_res = self.purchase_line_model.product_id_change(
                self.purchase_pricelist.id,
                product.id,
                qty,
                product.uom_id.id,
                self.partner1.id)
            line_values.update(onchange_res['value'])
            lines.append(
                (0, 0, line_values)
            )
        po = self.purchase_model.create({
            'partner_id': self.partner1.id,
            'location_id': self.location_stock.id,
            'pricelist_id': self.purchase_pricelist.id,
            'order_line': lines,
            'invoice_method': 'manual',
        })
        return po

    def test_ship_and_cancel_part(self):
        # We have 1000 product1
        # Ship 200 products
        self.ship([(self.product1, 200),
                   (self.product2, 0),
                   (self.product3, 0),
                   ])

        self.assert_moves([
            (self.product1, 200, 'done'),
            (self.product1, 800, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])

        # amend the purchase order
        amendment = self.amend()

        # keep only 300 product1 of the 800 expected
        self.amend_product(amendment, self.product1, 300)
        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product1, 500, 'confirmed'),
            (self.product1, 500, 'cancel'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ])
        self.assert_moves([
            (self.product1, 200, 'done'),
            (self.product1, 500, 'cancel'),
            (self.product1, 300, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])
        self.assertEqual(self.purchase.state, 'approved')

    def test_cancel_one_line(self):
        # amend the purchase order
        amendment = self.amend()
        # Remove product1
        self.amend_product(amendment, self.product1, 0)
        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product1, 1000, 'cancel'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ])
        self.assert_moves([
            (self.product1, 1000, 'cancel'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])
        self.assertEqual(self.purchase.state, 'approved')

    def test_ship_amend_more(self):
        # Ship 200 product1
        self.ship([(self.product1, 200),
                   (self.product2, 0),
                   (self.product3, 0),
                   ])

        # amend the purchase order
        amendment = self.amend()
        self.amend_product(amendment, self.product1, 2000)

        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product1, 2200, 'confirmed'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ])
        self.assert_moves([
            (self.product1, 200, 'done'),
            (self.product1, 2000, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])
        self.assertEqual(self.purchase.state, 'approved')

    def test_amend_nothing(self):
        # amend the purchase order
        amendment = self.amend()

        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product1, 1000, 'confirmed'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ])
        self.assert_moves([
            (self.product1, 1000, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])
        self.assertEqual(self.purchase.state, 'approved')

    def XXX_test_cancel_and_amend(self):
        # We do not handle that case at the moment. Maybe we can handle this
        # case recreating the moves manually.

        # Cancel all moves
        self.purchase.mapped('picking_ids.move_lines').action_cancel()

        self.assertEqual(self.purchase.state, 'except_picking')

        # amend the purchase order
        amendment = self.amend()

        # reset to original quantity
        self.amend_product(amendment, self.product1, 1000)
        self.amend_product(amendment, self.product2, 500)
        self.amend_product(amendment, self.product3, 800)

        amendment.do_amendment()
        self.assert_purchase_lines([
            (self.product1, 1000, 'confirmed'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ])
        self.assert_moves([
            (self.product1, 1000, 'cancel'),
            (self.product2, 500, 'cancel'),
            (self.product3, 800, 'cancel'),
            (self.product1, 1000, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ])

        self.assertEqual(self.purchase.state, 'approved')

    def test_amend_ship_all(self):
        amendment = self.amend()
        self.amend_product(amendment, self.product1, 500)
        self.amend_product(amendment, self.product2, 300)
        self.amend_product(amendment, self.product3, 300)
        amendment.do_amendment()
        self.assert_moves([
            (self.product1, 500, 'cancel'),
            (self.product1, 500, 'assigned'),
            (self.product2, 200, 'cancel'),
            (self.product2, 300, 'assigned'),
            (self.product3, 500, 'cancel'),
            (self.product3, 300, 'assigned'),
        ])
        self.ship([(self.product1, 500),
                   (self.product2, 300),
                   (self.product3, 300),
                   ])
        self.assert_moves([
            (self.product1, 500, 'cancel'),
            (self.product1, 500, 'done'),
            (self.product2, 200, 'cancel'),
            (self.product2, 300, 'done'),
            (self.product3, 500, 'cancel'),
            (self.product3, 300, 'done'),
        ])
        self.assertNotEqual(self.purchase.state, 'except_picking')

    def test_ship_partial_amend_ship_all(self):
        self.ship([(self.product1, 100),
                   (self.product2, 100),
                   (self.product3, 0),
                   ])
        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 900, 'assigned'),
            (self.product2, 400, 'assigned'),
            (self.product2, 100, 'done'),
            (self.product3, 800, 'assigned'),
        ])
        amendment = self.amend()
        self.amend_product(amendment, self.product1, 200)
        self.amend_product(amendment, self.product2, 200)
        self.amend_product(amendment, self.product3, 200)
        amendment.do_amendment()

        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 200, 'assigned'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'assigned'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'assigned'),
        ])

        self.ship([(self.product1, 200),
                   (self.product2, 200),
                   (self.product3, 200),
                   ])
        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 200, 'done'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'done'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'done'),
        ])
        self.assertNotEqual(self.purchase.state, 'except_picking')

    def test_ship_partial_amend_ship_partial_amend0(self):
        self.ship([(self.product1, 100),
                   (self.product2, 100),
                   (self.product3, 0),
                   ])
        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 900, 'assigned'),
            (self.product2, 400, 'assigned'),
            (self.product2, 100, 'done'),
            (self.product3, 800, 'assigned'),
        ])
        amendment = self.amend()
        self.amend_product(amendment, self.product1, 200)
        self.amend_product(amendment, self.product2, 200)
        self.amend_product(amendment, self.product3, 200)
        amendment.do_amendment()

        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 200, 'assigned'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'assigned'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'assigned'),
        ])

        self.ship([(self.product1, 110),
                   (self.product2, 120),
                   (self.product3, 130),
                   ])
        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 110, 'done'),
            (self.product1, 90, 'assigned'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 120, 'done'),
            (self.product2, 80, 'assigned'),
            (self.product3, 600, 'cancel'),
            (self.product3, 130, 'done'),
            (self.product3, 70, 'assigned'),
        ])
        amendment = self.amend()
        self.amend_product(amendment, self.product1, 0)
        self.amend_product(amendment, self.product2, 0)
        self.amend_product(amendment, self.product3, 0)
        amendment.do_amendment()
        self.assert_moves([
            (self.product1, 100, 'done'),
            (self.product1, 110, 'done'),
            (self.product1, 90, 'cancel'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 120, 'done'),
            (self.product2, 80, 'cancel'),
            (self.product3, 600, 'cancel'),
            (self.product3, 130, 'done'),
            (self.product3, 70, 'cancel'),
        ])
        self.assertNotEqual(self.purchase.state, 'except_picking')
