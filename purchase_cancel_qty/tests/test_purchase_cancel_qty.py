# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseCancelQty(TransactionCase):

    def setUp(self):
        super(TestPurchaseCancelQty, self).setUp()
        self.PurchaseOrderObj = self.env['purchase.order']
        self.PurchaseOrderLineObj = self.env['purchase.order.line']

        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_8 = self.env.ref('product.product_product_8')

    def test_01_purchase_order_cancel_qty(self):
        values = {
            'partner_id': self.partner_id.id,
            'date_planned': Datetime.now(),
            'order_line': [
                (0, 0, {
                    'name': self.product_8.name,
                    'product_id': self.product_8.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_8.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': Datetime.now(),
                }),
            ]
        }
        purchase_order = self.PurchaseOrderObj.create(values)
        po_line_1 = purchase_order.order_line[0]

        purchase_order.button_approve()
        self.assertTrue(all([
            line.ordered_qty == line.product_qty
            for line in purchase_order.order_line
        ]), msg="Initially ordered quantity should have been "
                "initialized with product quantity")

        po_line_1.cancelled_qty = 2
        self.assertEqual(po_line_1.product_qty, 3)
        self.assertEqual(
            po_line_1.ordered_qty - po_line_1.cancelled_qty,
            po_line_1.product_qty)

        with self.assertRaises(ValidationError):
            po_line_1.cancelled_qty = 6

        purchase_order.write({
            'order_line': [
                (0, 0, {
                    'name': self.product_8.name,
                    'product_id': self.product_8.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_8.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': Datetime.now(),
                }),
            ]
        })

        po_line_2 = purchase_order.order_line[1]
        self.assertEqual(
            po_line_2.ordered_qty, po_line_2.product_qty,
            msg="Ordered quantity should have been initialized with "
                "product quantity.")
