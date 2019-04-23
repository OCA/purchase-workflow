# Copyright 2019 Akretion - Renato Lima (<http://akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from odoo.tests import common


class TestPurchaseOrderRevision(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderRevision, self).setUp()
        self.purchase_order_model = self.env['purchase.order']
        self.partner_id = self.env.ref('base.res_partner_2').id
        self.product_id25 = self.env.ref('product.product_product_25').id
        self.product_unit = self.env.ref('uom.product_uom_unit').id
        self.purchase_order_1 = self._create_purchase_order()
        self.action = self._revision_purchase_order(self.purchase_order_1)
        self.revision_1 = self.purchase_order_1.current_revision_id

    def _create_purchase_order(self):
        # Creating a purchase order
        new_purchase = self.purchase_order_model.create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.product_id25,
                'name': 'Acoustic Bloc Screens',
                'price_unit': 2868.70,
                'product_qty': '15.0',
                'product_uom': self.product_unit,
                'date_planned': time.strftime('%Y-%m-%d')
            })]
        })
        return new_purchase

    def _revision_purchase_order(self, purchase_order):
        # Cancel the purchase order
        purchase_order.button_cancel()
        # Create a new revision
        return purchase_order.create_revision()

    def test_order_revision(self):
        """Check revision process"""
        self.assertEqual(self.purchase_order_1.unrevisioned_name,
                         self.purchase_order_1.name)
        self.assertEqual(self.purchase_order_1.state, 'cancel')
        self.assertFalse(self.purchase_order_1.active)
        self.assertEqual(self.revision_1.unrevisioned_name,
                         self.purchase_order_1.name)
        self.assertEqual(self.revision_1.state, 'draft')
        self.assertTrue(self.revision_1.active)
        self.assertEqual(self.revision_1.old_revision_ids,
                         self.purchase_order_1)
        self.assertEqual(self.revision_1.revision_number, 1)
        self.assertEqual(self.revision_1.name.endswith('-01'), True)
        self.assertEqual(self.revision_1.has_old_revisions, True)

        self._revision_purchase_order(self.revision_1)
        revision_2 = self.revision_1.current_revision_id

        self.assertEqual(revision_2.has_old_revisions, True)

        self.assertEqual(revision_2,
                         self.purchase_order_1.current_revision_id)
        self.assertEqual(self.revision_1.state, 'cancel')
        self.assertFalse(self.revision_1.active)
        self.assertEqual(revision_2.unrevisioned_name,
                         self.purchase_order_1.name)
        self.assertEqual(revision_2.state, 'draft')
        self.assertTrue(revision_2.active)
        self.assertEqual(revision_2.old_revision_ids,
                         self.purchase_order_1 + self.revision_1)
        self.assertEqual(revision_2.revision_number, 2)
        self.assertEqual(revision_2.name.endswith('-02'), True)

    def test_simple_copy(self):
        purchase_order_2 = self._create_purchase_order()
        self.assertEqual(purchase_order_2.name,
                         purchase_order_2.unrevisioned_name)
        purchase_order_3 = purchase_order_2.copy()
        self.assertEqual(purchase_order_3.name,
                         purchase_order_3.unrevisioned_name)
