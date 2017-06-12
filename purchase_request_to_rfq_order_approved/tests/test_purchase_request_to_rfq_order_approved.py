# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests import common
from openerp.tools import SUPERUSER_ID


class TestPurchaseRequestToRfqOrderApproved(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRfqOrderApproved, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz =\
            self.env['purchase.request.line.make.purchase.order']
        self.purchase_order = self.env['purchase.order']

    def test_purchase_request_to_purchase_rfq_multiple_PO(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        purchase_request1.company_id.purchase_approve_active = True
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request1.id,
            'product_id': self.env.ref('product.product_product_6').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 2.0,
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
            if item.line_id.id == purchase_request_line1.id:
                item.product_qty = 1
            if item.line_id.id == purchase_request_line2.id:
                item.keep_description = True
            if item.line_id.id == purchase_request_line3.id:
                item.onchange_product_id()
        wiz_id.make_purchase_order()
        purchase = purchase_request_line1.purchase_lines[0].order_id
        purchase.button_confirm()

        self.assertEquals(purchase_request_line1.purchase_state, 'approved',
                          'Status of the request line should be approved')

        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id]).create(vals)
        for item in wiz_id.item_ids:
            if item.line_id.id == purchase_request_line1.id:
                item.product_qty = 1
        wiz_id.make_purchase_order()
        purchase = purchase_request_line1.purchase_lines[0].order_id
        purchase.button_confirm()
        self.assertEquals(purchase_request_line1.purchase_state, 'approved',
                          'Status of the request line should be approved')
        purchase.button_release()
        self.assertEquals(purchase_request_line1.purchase_state, 'purchase',
                          'Status of the request line should be purchase')
