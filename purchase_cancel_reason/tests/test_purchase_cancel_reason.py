# -*- coding: utf-8 -*-
# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseCancelReason(TransactionCase):

    def setUp(self):
        super(TestPurchaseCancelReason, self).setUp()
        PurchaseOrder = self.env['purchase.order']
        CancelReason = self.env['purchase.order.cancel.reason']
        self.reason = CancelReason.create({'name': 'Canceled for tests'})
        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        self.product = self.env['product.product'].create({
            'name': 'Product'
        })
        uom = self.env.ref('product.product_uom_unit')
        self.purchase_order = PurchaseOrder.create({
            'partner_id': self.supplier.id,
            'date_planned': fields.Datetime.now(),
            'order_line': [(0, 0, {
                'name': 'Line 1',
                'product_id': self.product.id,
                'product_qty': 8,
                'product_uom': uom.id,
                'price_unit': 100.00,
                'date_planned': fields.Datetime.now(),
            })],
        })

    def test_purchase_order_cancel_reason(self):
        """
        - Cancel a purchase order with the wizard asking for the reason
        - Then the purchase order should be canceled and the reason stored
        """
        PurchaseOrderCancel = self.env['purchase.order.cancel']
        context = {'active_model': 'purchase.order',
                   'active_ids': [self.purchase_order.id], }
        wizard = PurchaseOrderCancel.create({'reason_id': self.reason.id})
        wizard.with_context(context).confirm_cancel()
        self.assertEqual(self.purchase_order.state, 'cancel',
                         'the purchase order should be canceled')
        self.assertEqual(self.purchase_order.cancel_reason_id.id,
                         self.reason.id)
