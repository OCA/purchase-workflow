# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPreparePurchaseOrder(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestPreparePurchaseOrder, self).setUp(*args, **kwargs)
        # Objects
        self.obj_purchase_requisition = self.env['purchase.requisition']
        self.obj_purchase_order_type = self.env['purchase.order.type']
        self.obj_purchase_order = self.env['purchase.order']

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
        # Create Purchase Requisition
        data_purchase_requisition = self._prepare_purchase_requisition()
        purchase_requisition = self.obj_purchase_requisition.\
            create(data_purchase_requisition)

        # Check Create Purchase Requisition
        self.assertIsNotNone(purchase_requisition)

        # Create Purchase Order For Purchase Requitition
        po = purchase_requisition.make_purchase_order(self.supplier.id)

        # Check Create Purchase Order
        self.assertIsNotNone(po)

        # Check method _prepare_purchase_order
        po_id = po[purchase_requisition.id]

        data_po = self.obj_purchase_order.browse(po_id)[0]

        self.assertEqual(data_po.order_type.id, self.order_type.id)
        self.assertEqual(
            data_po.invoice_method, self.order_type.invoice_method)
