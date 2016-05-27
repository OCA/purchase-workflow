# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common
from openerp.tools import SUPERUSER_ID


class TestPurchaseRequest(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequest, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']

    def test_purchase_request_status(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        self.purchase_request_line.create(vals)
        purchase_request.button_to_approve()
        self.assertEqual(
            purchase_request.state, 'to_approve',
            'Should be in state to_approve')
        purchase_request.button_draft()
        self.assertEqual(
            purchase_request.state, 'draft',
            'Should be in state draft')
        self.purchase_request_line.unlink()
