# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests import common
from openerp.tools import SUPERUSER_ID
from openerp import fields


class TestPurchaseRequestToRfq(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz = self.env['purchase.request.line.make.purchase.order']
        self.purchase_order = self.env['purchase.order']
        self.po_line = self.env['purchase.order.line']

        self.product = self.env.ref('product.product_product_13')
        self.partner = self.env.ref('base.res_partner_1')

        self.pr_vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        proc_vals = {
            'name': 'test procurement',
            'date_planned': fields.Datetime.now(),
            'product_id': self.product.id,
            'product_qty': 4.0,
            'product_uom': self.product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (4, self.env.ref('purchase.route_warehouse0_buy').id, 0)],
        }
        self.proc = self.env['procurement.order'].create(proc_vals)

    def test_purchase_request_to_purchase_rfq(self):
        purchase_request = self.purchase_request.create(self.pr_vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.product.id,
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
        purchase_request = self.purchase_request.create(self.pr_vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.product.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        request_lines = purchase_request_line + purchase_request_line.copy()
        request_lines.mapped('is_editable')

        # Test also for onchanges on non created lines
        self.purchase_request_line.new({}).is_editable

    def test_purchase_request_to_purchase_rfq_minimum_order_qty(self):
        purchase_request = self.purchase_request.create(self.pr_vals)
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
        purchase_request1 = self.purchase_request.create(self.pr_vals)
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

    def test_purchase_request_to_purchase_rfq_multiple_PO_purchaseUoM(self):
        product = self.env.ref('product.product_product_6')
        product.uom_po_id = self.env.ref('product.product_uom_dozen')

        purchase_request1 = self.purchase_request.create(self.pr_vals)
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request1.id,
            'product_id': product.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 12.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            'request_id': purchase_request2.id,
            'product_id': product.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 12.0,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        vals = {
            'request_id': purchase_request2.id,
            'product_id': self.env.ref('product.product_product_6').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 12.0,
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
        po_line = purchase_request_line1.purchase_lines[0]
        self.assertEquals(po_line.product_qty, 2.0, 'Quantity should be 2')
        self.assertEquals(po_line.product_uom,
                          self.env.ref('product.product_uom_dozen'),
                          'The purchase UoM should be Dozen(s).')

    def test_po_cancellation(self):
        """Tests the cancellation of a purchase order without lines related
        to a purchase request."""
        if self.registry.get('purchase.requisition') is not None:
            req_id = self.proc.requisition_id.id
            req_wiz = self.env['purchase.requisition.partner'].create(
                {'partner_ids': [(6, 0, self.partner.ids)]})
            req_wiz.with_context(active_ids=[req_id]).create_order()
            po = self.purchase_order.search(
                [('requisition_id', '=', req_id)], limit=1)
        else:
            po = self.proc.purchase_id
        po.button_confirm()
        po.button_cancel()
        self.assertEqual(po.state, 'cancel', "PO hasn't been cancelled.")
        if self.registry.get('purchase.requisition') is None:
            self.assertEqual(self.proc.state, 'cancel',
                             "procurement hasn't been cancelled.")

    def test_mixed_po_cancellation(self):
        """Tests cancellation of purchase order with a line related to a
        purchase request."""
        purchase_request = self.purchase_request.create(self.pr_vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.product.id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        purchase_request_line = self.purchase_request_line.create(vals)
        purchase_request.button_to_approve()
        purchase_request.button_approved()
        if self.registry.get('purchase.requisition') is not None:
            po = self.purchase_order.create({
                'partner_id': self.partner.id,
            })
            self.po_line.create({
                'date_planned': fields.Datetime.now(),
                'name': 'test po line',
                'order_id': po.id,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'price_unit': 1.0,
                'product_qty': 5.0,
            })
        else:
            po = self.proc.purchase_id
        vals = {
            'purchase_order_id': po.id,
        }
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,).create(vals)
        wiz_id.make_purchase_order()
        self.assertGreaterEqual(len(po.order_line), 2)
        po.button_confirm()
        po.button_cancel()
        self.assertEqual(po.state, 'cancel', "PO hasn't been cancelled.")
        if self.registry.get('purchase.requisition') is None:
            self.assertEqual(self.proc.state, 'cancel',
                             "procurement hasn't been cancelled.")
        self.assertFalse(purchase_request_line.cancelled)
        self.assertNotEqual(purchase_request.state, 'cancel')
