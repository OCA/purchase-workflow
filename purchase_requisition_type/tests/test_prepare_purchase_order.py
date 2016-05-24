# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPreparePurchaseOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestPreparePurchaseOrder, self).setUp(*args, **kwargs)
        # Objects
        self.obj_purchase_requisition = self.env['purchase.requisition']

        # Data Products
        self.prod_1 = self.env.ref('product.product_product_8')
        self.prod_2 = self.env.ref('product.product_product_9')
        self.uom = self.env.ref('product.product_uom_unit')

        # Data Supplier
        self.supplier = self.env.ref('base.res_partner_2')

        # Data Order Type
        self.order_type = self.env.ref('purchase_order_type.po_type_contract')

    def _prepare_purchase_requisition(self):
        data = {
            'exclusive': 'exclusive',
            'line_ids': [
                (0, 0, {'product_id': self.prod_1.id,
                        'product_qty': 5.0,
                        'product_uom_id': self.uom.id}),
                (0, 0, {'product_id': self.prod_2.id,
                        'product_qty': 5.0,
                        'product_uom_id': self.uom.id})
            ],
            'order_type': self.order_type.id
        }
        return data

    def test_prepare_purchase_order(self):
        x = []
        # Create Purchase Requisition
        data_purchase_requisition = self._prepare_purchase_requisition()
        purchase_requisition = self.obj_purchase_requisition.\
            create(data_purchase_requisition)

        # Check Create Purchase Requisition
        self.assertIsNotNone(purchase_requisition)

        # Check Purchase Term
        self.assertIsNotNone(x)

        # Check Prepare Purchase Order
        data_prepare_po = self.obj_purchase_requisition.\
            _prepare_purchase_order(purchase_requisition, self.supplier)

        order_type = data_prepare_po.get('order_type')

        self.assertEqual(order_type, self.order_type.id)
        self.assertEqual(order_type, self.order_type.invoice_method)
