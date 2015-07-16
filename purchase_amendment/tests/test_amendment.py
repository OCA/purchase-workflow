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
from openerp import netsvc


class TestAmendmentCombinations(common.TransactionCase, AmendmentMixin):

    def setUp(self):
        super(TestAmendmentCombinations, self).setUp()
        cr, uid, context = self.cr, self.uid, {}
        self.amendment_model = self.registry('purchase.order.amendment')
        self.purchase_model = self.registry('purchase.order')
        self.purchase_line_model = self.registry('purchase.order.line')
        data_model = self.registry('ir.model.data')
        _, partner1_id = data_model.get_object_reference(cr, uid, 'base',
                                                         'res_partner_1')
        self.partner1 = self.registry('res.partner').browse(cr, uid,
                                                            partner1_id,
                                                            context=context)
        _, product1_id = data_model.get_object_reference(
            cr, uid, 'product', 'product_product_7')
        self.product1 = self.registry('product.product').browse(
            cr, uid, product1_id, context=context)

        _, product2_id = data_model.get_object_reference(cr, uid, 'product',
                                                         'product_product_9')
        self.product2 = self.registry('product.product').browse(
            cr, uid, product2_id, context=context)

        _, product3_id = data_model.get_object_reference(
            cr, uid, 'product', 'product_product_11')
        self.product3 = self.registry('product.product').browse(
            cr, uid, product3_id, context=context)

        _, location_stock_id = data_model.get_object_reference(
            cr, uid, 'stock', 'stock_location_stock')
        self.location_stock = self.registry('stock.location').browse(
            cr, uid, location_stock_id, context=context)

        _, purchase_pricelist_id = data_model.get_object_reference(
            cr, uid, 'purchase', 'list0')
        self.purchase_pricelist = self.registry('product.pricelist').browse(
            cr, uid, purchase_pricelist_id, context=context)

        purchase_id = self._create_purchase(
            cr, uid, [(self.product1, 1000), (self.product2, 500),
                      (self.product3, 800)], context=context)
        self.purchase = self.registry('purchase.order').browse(
            cr, uid, purchase_id, context=context)

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', purchase_id,
                                'purchase_confirm', cr)

    def _create_purchase(self, cr, uid, line_products, context=None):
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
            onchange_res = self.purchase_line_model.onchange_product_id(
                cr, uid, [], self.purchase_pricelist.id, product.id, qty,
                product.uom_id.id, self.partner1.id, context=context)
            line_values.update(onchange_res['value'])
            lines.append(
                (0, 0, line_values)
            )
        po = self.purchase_model.create(cr, uid, {
            'partner_id': self.partner1.id,
            'location_id': self.location_stock.id,
            'pricelist_id': self.purchase_pricelist.id,
            'order_line': lines,
            'invoice_method': 'manual',
        }, context=context)
        return po

    def test_ship_and_cancel_part(self):
        # We have 1000 product1
        # Ship 200 products
        cr, uid, context = self.cr, self.uid, {}
        self.ship(cr, uid, [(self.product1, 200), (self.product2, 0),
                            (self.product3, 0)],
                  context=context)

        self.assert_moves(cr, uid, [
            (self.product1, 200, 'done'),
            (self.product1, 800, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ], context=context)

        # amend the purchase order
        amendment = self.amend(cr, uid, context=context)

        # keep only 300 product1 of the 800 expected
        amendment = self.amend_product(cr, uid, amendment, self.product1, 300,
                                       context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_purchase_lines(cr, uid, [
            (self.product1, 500, 'confirmed'),
            (self.product1, 500, 'cancel'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 200, 'done'),
            (self.product1, 500, 'cancel'),
            (self.product1, 300, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        self.assertEqual(self.purchase.state, 'approved')

    def test_cancel_one_line(self):
        # amend the purchase order
        cr, uid, context = self.cr, self.uid, {}
        amendment = self.amend(cr, uid, context=context)
        # Remove product1
        amendment = self.amend_product(cr, uid, amendment, self.product1, 0,
                           context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_purchase_lines(cr, uid, [
            (self.product1, 1000, 'cancel'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 1000, 'cancel'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        self.assertEqual(self.purchase.state, 'approved')

    def test_ship_amend_more(self):
        # Ship 200 product1
        cr, uid, context = self.cr, self.uid, {}
        self.ship(cr, uid, [(self.product1, 200), (self.product2, 0),
                            (self.product3, 0)], context=context)

        # amend the purchase order
        amendment = self.amend(cr, uid, context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product1, 2000,
                           context=context)

        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_purchase_lines(cr, uid, [
            (self.product1, 2200, 'confirmed'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 200, 'done'),
            (self.product1, 2000, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        self.assertEqual(self.purchase.state, 'approved')

    def test_amend_nothing(self):
        # amend the purchase order
        cr, uid, context = self.cr, self.uid, {}
        amendment = self.amend(cr, uid, context=context)

        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_purchase_lines(cr, uid, [
            (self.product1, 1000, 'confirmed'),
            (self.product2, 500, 'confirmed'),
            (self.product3, 800, 'confirmed'),
        ], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 1000, 'assigned'),
            (self.product2, 500, 'assigned'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        self.assertEqual(self.purchase.state, 'approved')

    def test_amend_ship_all(self):
        cr, uid, context = self.cr, self.uid, {}
        amendment = self.amend(cr, uid, context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product1, 500,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product2, 300,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product3, 300,
                           context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 500, 'cancel'),
            (self.product1, 500, 'assigned'),
            (self.product2, 200, 'cancel'),
            (self.product2, 300, 'assigned'),
            (self.product3, 500, 'cancel'),
            (self.product3, 300, 'assigned'),
        ], context=context)
        self.ship(cr, uid, [(self.product1, 500),
                            (self.product2, 300),
                            (self.product3, 300)], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 500, 'cancel'),
            (self.product1, 500, 'done'),
            (self.product2, 200, 'cancel'),
            (self.product2, 300, 'done'),
            (self.product3, 500, 'cancel'),
            (self.product3, 300, 'done'),
        ], context=context)
        self.assertNotEqual(self.purchase.state, 'except_picking')

    def test_ship_partial_amend_ship_all(self):
        cr, uid, context = self.cr, self.uid, {}
        self.ship(cr, uid, [(self.product1, 100),
                            (self.product2, 100),
                            (self.product3, 0)], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 100, 'done'),
            (self.product1, 900, 'assigned'),
            (self.product2, 400, 'assigned'),
            (self.product2, 100, 'done'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        amendment = self.amend(cr, uid, context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product1, 200,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product2, 200,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product3, 200,
                           context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 100, 'done'),
            (self.product1, 200, 'assigned'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'assigned'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'assigned'),
        ], context=context)

        self.ship(cr, uid, [(self.product1, 200),
                            (self.product2, 200),
                            (self.product3, 200)], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 100, 'done'),
            (self.product1, 200, 'done'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'done'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'done'),
        ], context=context)
        self.assertNotEqual(self.purchase.state, 'except_picking')

    def test_ship_partial_amend_ship_partial_amend0(self):
        cr, uid, context = self.cr, self.uid, {}
        self.ship(cr, uid, [(self.product1, 100),
                            (self.product2, 100),
                            (self.product3, 0)], context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 100, 'done'),
            (self.product1, 900, 'assigned'),
            (self.product2, 400, 'assigned'),
            (self.product2, 100, 'done'),
            (self.product3, 800, 'assigned'),
        ], context=context)
        amendment = self.amend(cr, uid, context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product1, 200,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product2, 200,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product3, 200,
                           context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_moves(cr, uid, [
            (self.product1, 100, 'done'),
            (self.product1, 200, 'assigned'),
            (self.product1, 700, 'cancel'),
            (self.product2, 200, 'cancel'),
            (self.product2, 100, 'done'),
            (self.product2, 200, 'assigned'),
            (self.product3, 600, 'cancel'),
            (self.product3, 200, 'assigned'),
        ], context=context)

        self.ship(cr, uid, [(self.product1, 110),
                            (self.product2, 120),
                            (self.product3, 130)], context=context)
        self.assert_moves(cr, uid, [
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
        ], context=context)
        amendment = self.amend(cr, uid, context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product1, 0,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product2, 0,
                           context=context)
        amendment = self.amend_product(cr, uid, amendment, self.product3, 0,
                           context=context)
        self.amendment_model.do_amendment(cr, uid, [amendment.id],
                                          context=context)
        self.assert_moves(cr, uid, [
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
        ], context=context)
        self.assertNotEqual(self.purchase.state, 'except_picking')
