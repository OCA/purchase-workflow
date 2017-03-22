# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests import common
from openerp.tools import SUPERUSER_ID


class TestPurchaseRequestToRfq(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz =\
            self.env['purchase.request.line.make.purchase.order']
        self.purchase_order = self.env['purchase.order']

    def test_purchase_request_to_purchase_rfq(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        purchase_request.button_to_approve()
        purchase_request.button_approved()

        vals = {
            'supplier_id': self.env.ref('base.res_partner_12').id,
        }
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,).create(vals)
        wiz_id.make_purchase_order()
        self.assertTrue(
            len(purchase_request_line.purchase_lines),
            'Should have a purchase line')
        self.assertEquals(
            purchase_request_line.purchase_lines.product_id.id,
            purchase_request_line.product_id.id,
            'Should have same product')
        self.assertEquals(
            purchase_request_line.purchase_lines.state,
            purchase_request_line.purchase_state,
            'Should have same state')

    def test_bug_is_editable_multiple_lines(self):
        # Check that reading multiple lines is still possible
        # https://github.com/OCA/purchase-workflow/pull/291
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        request_lines = purchase_request_line + purchase_request_line.copy()
        request_lines.mapped('is_editable')

        # Test also for onchanges on non created lines
        self.purchase_request_line.new({}).is_editable

    def test_purchase_request_to_purchase_rfq_minimum_order_qty(self):

        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_8').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 1.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        vals = {
            'supplier_id': self.env.ref('base.res_partner_1').id,
        }
        purchase_request.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,).create(vals)
        wiz_id.make_purchase_order()
        self.assertTrue(
            len(purchase_request_line.purchase_lines),
            'Should have a purchase line')
        self.assertEquals(
            purchase_request_line.purchase_lines.product_id.id,
            purchase_request_line.product_id.id,
            'Should have same product')
        self.assertEquals(
            purchase_request_line.purchase_lines.state,
            purchase_request_line.purchase_state,
            'Should have same state')
        self.assertEquals(
            purchase_request_line.purchase_lines.product_qty,
            5,
            'The PO line should have the minimum order quantity.')
        self.assertEquals(
            purchase_request_line,
            purchase_request_line.purchase_lines.purchase_request_lines,
            'The PO should cross-reference to the purchase request.')

    def test_purchase_request_to_purchase_rfq_multiple_PO(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request1.id,
            'product_id': self.env.ref('product.product_product_6').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 1.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            'request_id': purchase_request2.id,
            'product_id': self.env.ref('product.product_product_6').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 1.0,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        vals = {
            'request_id': purchase_request2.id,
            'product_id': self.env.ref('product.product_product_6').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 1.0,
        }
        purchase_request_line3 = self.purchase_request_line.create(vals)
        vals = {
            'supplier_id': self.env.ref('base.res_partner_1').id,
        }
        purchase_request1.button_approved()
        purchase_request2.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id, purchase_request_line2.id,
                        purchase_request_line3.id]).create(vals)
        for item in wiz_id.item_ids:
            if item.line_id.id == purchase_request_line2.id:
                item.keep_description = True
            if item.line_id.id == purchase_request_line3.id:
                item.onchange_product_id()
        wiz_id.make_purchase_order()
        self.assertEquals(purchase_request_line1.purchased_qty, 2.0,
                          'Should be a quantity of 2')
        self.assertEquals(purchase_request_line2.purchased_qty, 1.0,
                          'Should be a quantity of 1')
