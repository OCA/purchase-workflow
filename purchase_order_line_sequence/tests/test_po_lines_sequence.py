# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tests import common


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env['purchase.order']
        self.Invoice = self.env['account.invoice']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.InvoiceLine = self.env['account.invoice.line']
        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_id_1 = self.env.ref('product.product_product_8')
        self.product_id_2 = self.env.ref('product.product_product_11')

    def _create_purchase_order(self):
        po_vals = {
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': datetime.today().
                    strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                    'price_unit': 250.0,
                    'date_planned': datetime.today().
                    strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }

        return self.PurchaseOrder.create(po_vals)

    def test_purchase_order_line_sequence(self):

        self.po = self._create_purchase_order()
        self.po.button_confirm()

        move1 = self.env['stock.move'].\
            search([('purchase_line_id', '=', self.po.order_line[0].id)])
        move2 = self.env['stock.move'].\
            search([('purchase_line_id', '=', self.po.order_line[1].id)])

        self.assertEqual(self.po.order_line[0].sequence,
                         move1.sequence,
                         'The Sequence of the Purchase Order Lines does not '
                         'match to the Stock Moves')
        self.assertEqual(self.po.order_line[1].sequence,
                         move2.sequence,
                         'The Sequence of the Purchase Order Lines does not '
                         'match to the Stock Moves')

        self.po2 = self.po.copy()
        self.assertEqual(self.po.order_line[0].sequence,
                         self.po2.order_line[0].sequence,
                         'The Sequence is not copied properly')
        self.assertEqual(self.po.order_line[1].sequence,
                         self.po2.order_line[1].sequence,
                         'The Sequence is not copied properly')

    def test_invoice_sequence(self):

        po = self._create_purchase_order()
        po.button_confirm()
        po.picking_ids.do_transfer()

        invoice = self.Invoice.create({'partner_id': self.partner_id.id})
        invoice.purchase_id = po.id
        invoice.currency_id = self.env.ref('base.INR').id,
        invoice.purchase_order_change()

        self.assertEqual(po.order_line[0].sequence,
                         invoice.invoice_line_ids[0].sequence,
                         'The Sequence is not copied properly')
        self.assertEqual(po.order_line[1].sequence,
                         invoice.invoice_line_ids[1].sequence,
                         'The Sequence is not copied properly')
