# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductCustomerCodePurchase(TransactionCase):

    def setUp(self):
        super(TestProductCustomerCodePurchase, self).setUp()
        # Useful models
        self.PurchaseOrder = self.env['purchase.order']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.ProductCustomerCode = self.env['product.customer.code']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']

    def test_00_purchase_customer_code(self):
        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_id = self.env.ref('product.product_product_11')

        self.ProductCustomerCode.create(
            {
                'product_name': self.product_id.name +
                '4' + self.partner_id.name,
                'product_code': 'code01',
                'product_id': self.product_id.id,
                'partner_id': self.partner_id.id
            }
        )
        po_vals = {
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id.name,
                    'product_id': self.product_id.id,
                    'product_qty': 1.0,
                    'product_uom': self.product_id.uom_po_id.id,
                    'price_unit': 1.0,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        }
        self.po = self.PurchaseOrder.create(po_vals)
        self.assertTrue(self.po, 'No purchase order created')
        self.assertTrue(
            self.po.order_line and self.po.order_line[0],
            'No purchase order line created')
        self.assertEqual(
            self.po.order_line[0].product_customer_code, 'code01',
            'PO line customer code should be "code01"')
