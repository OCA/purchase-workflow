# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tests import common


class TestPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env['purchase.order']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']

    def test_purchase_order(self):
        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_id_1 = self.env.ref('product.product_product_8')
        self.product_id_2 = self.env.ref('product.product_product_11')

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
        self.po = self.PurchaseOrder.create(po_vals)

        self.po.button_confirm()
        self.assertEqual(self.po.state,
                         'purchase',
                         'Purchase: PO state should be "Purchase"')
        self.assertEqual(self.po.invoice_status,
                         'to invoice',
                         'PO invoice_status should be "Waiting Invoices"')
        self.assertEqual(self.po.picking_count, 1,
                         'Purchase: one picking should be created"')
        self.picking = self.po.picking_ids[0]
        self.picking.force_assign()
        self.picking.pack_operation_product_ids.write({'qty_done': 5.0})
        self.picking.do_new_transfer()
        self.assertEqual(self.po.order_line.mapped('qty_received'),
                         [5.0, 5.0],
                         'Purchase: all products should be received"')

        self.invoice = self.AccountInvoice.create({
            'partner_id': self.partner_id.id,
            'purchase_id': self.po.id,
            'account_id': self.partner_id.property_account_payable_id.id,
        })
        self.invoice.purchase_order_change()
        self.assertEqual(self.po.order_line.mapped('qty_invoiced'),
                         [5.0, 5.0],
                         'Purchase: all products should be invoiced"')
