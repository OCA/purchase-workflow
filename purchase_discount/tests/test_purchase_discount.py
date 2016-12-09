# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import workflow, fields


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.product_1 = self.env.ref('product.product_product_4')
        self.product_2 = self.env.ref('product.product_product_5b')
        po_model = self.env['purchase.order.line']
        self.purchase_order = self.env['purchase.order'].create(
            {'partner_id': self.env.ref('base.res_partner_3').id,
             'pricelist_id': self.env.ref('purchase.list0').id,
             'location_id': self.env.ref('stock.stock_location_stock').id})
        self.po_line_1 = po_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product_1.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1.0,
             'discount': 50.0,
             'price_unit': 10.0})
        self.tax = self.env['account.tax'].create(
            {'name': 'Sample tax 15%',
             'type': 'percent',
             'amount': 0.15})
        self.po_line_2 = po_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product_2.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 10.0,
             'discount': 30,
             'taxes_id': [(6, 0, [self.tax.id])],
             'price_unit': 230.0})

    def test_purchase_order_vals(self):
        self.assertEqual(self.po_line_1.price_subtotal, 5.0)
        self.assertEqual(self.po_line_2.price_subtotal, 1610.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1615.0)
        self.assertEqual(self.purchase_order.amount_tax, 241.5)

    def test_make_invoice_draft_invoice(self):
        self.purchase_order.invoice_method = 'order'
        workflow.trg_validate(
            self.uid, 'purchase.order', self.purchase_order.id,
            'purchase_confirm', self.cr)
        self.assertEqual(self.po_line_1.invoice_lines.discount, 50)
        self.assertEqual(self.po_line_2.invoice_lines.discount, 30)

    def test_make_invoice_from_picking(self):
        self.purchase_order.invoice_method = 'picking'
        workflow.trg_validate(
            self.uid, 'purchase.order', self.purchase_order.id,
            'purchase_confirm', self.cr)
        invoice_ids = self.purchase_order.picking_ids.action_invoice_create(
            self.env.ref('account.expenses_journal').id, type='in_invoice')
        invoice = self.env['account.invoice'].browse(invoice_ids[0])
        self.assertEqual(invoice.invoice_line[0].discount, 50)
        self.assertEqual(invoice.invoice_line[1].discount, 30)

    def test_make_invoice_from_returned_picking(self):
        self.purchase_order.invoice_method = 'picking'
        workflow.trg_validate(
            self.uid, 'purchase.order', self.purchase_order.id,
            'purchase_confirm', self.cr)
        self.purchase_order.picking_ids.do_transfer()
        picking = self.purchase_order.picking_ids[0]
        move = picking.move_lines[0]
        wiz = self.env['stock.return.picking'].with_context(
            active_id=picking.id).create(
            {'invoice_state': '2binvoiced'})
        wiz.with_context(active_id=picking.id).create_returns()
        returned_picking = self.env['stock.move'].search(
            [('origin_returned_move_id', '=', move.id)])[0].picking_id
        invoice_ids = returned_picking.action_invoice_create(
            self.env.ref('account.expenses_journal').id, type='in_invoice')
        invoice = self.env['account.invoice'].browse(invoice_ids[0])
        self.assertEqual(invoice.invoice_line[0].discount, 50)
        self.assertEqual(invoice.invoice_line[1].discount, 30)
