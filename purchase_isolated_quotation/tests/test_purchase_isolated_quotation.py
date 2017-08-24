# -*- coding: utf-8 -*-
# © 2017 Ecosoft (ecosoft.co.th).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestPurchaseIsolatedQuotation(TransactionCase):

    def test_purchase_isolated_quotation(self):
        """
        - New purchase.order will have order_type = 'quotation'
        - When quotation is converted to order
          - Status chagned to 'done'
          - New purchase.order of order_type = 'purchase_order' created
        - Quotation can refer to Order and Order can refer to Quotation
        """
        self.quotation.action_convert_to_order()
        self.assertEqual(self.quotation.state, 'done')
        self.purchase_order = self.quotation.order_id
        self.assertTrue(self.purchase_order.is_order)
        self.assertEqual(self.purchase_order.state, 'draft')
        self.assertEqual(self.purchase_order.partner_id, self.partner)
        self.assertEqual(self.purchase_order.quote_id, self.quotation)

    def setUp(self):
        super(TestPurchaseIsolatedQuotation, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        vals = {
            'partner_id': self.partner.id,
            'is_order': False,
        }
        self.quotation = self.env['purchase.order'].create(vals)
