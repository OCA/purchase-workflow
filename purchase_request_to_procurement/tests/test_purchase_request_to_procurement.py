# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import SUPERUSER_ID


class TestPurchaseRequestToProcurement(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToProcurement, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.p_order = self.env['procurement.order']

    def test_generate_procurement_order(self):
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
        line = self.purchase_request_line.create(vals)
        p_order = self.p_order.browse(line._generate_procurement_order())
        self.assertEquals(
            p_order.name,
            purchase_request.name,
            'Should have the same name')
        self.assertTrue(
            p_order.location_id, 'Procurements must be created with a '
                                 'location always. Even if not explicitly '
                                 'defined.')
        self.assertTrue(
            p_order.warehouse_id, 'Procurements must be created with a '
                                  'warehouse always.')
        vals = {
            'location_id': self.env['stock.location'].search([], limit=1).id,
            'warehouse_id': self.env['stock.warehouse'].search([], limit=1).id,
        }
        purchase_request.write(vals)
        p_order = self.p_order.browse(line._generate_procurement_order())
        self.assertEquals(
            vals['location_id'],
            p_order.location_id.id,
            'Should be the same')
        self.assertEquals(
            vals['warehouse_id'],
            p_order.warehouse_id.id,
            p_order.warehouse_id.id)

    def test_make_procurement_order(self):
        """
        test generation of procurement order
        """
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
            'location_id': self.env['stock.location'].search([], limit=1).id,
            'warehouse_id': self.env['stock.warehouse'].search([], limit=1).id,
            'state': 'approved',
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.env.ref('product.product_product_13').id,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'product_qty': 5.0,
        }
        line = self.purchase_request_line.create(vals)
        ctx = {
            'active_ids': [line.id],
            'active_id': line.id,
            'active_model': 'purchase.request.line',
        }
        wiz_mod = self.env['purchase.request.line.make.procurement.order']
        wiz_id = wiz_mod.with_context(ctx).create({})
        res = wiz_id.make_procurement_order()
        procurement_ids = res['domain'][0][2]
        self.assertEquals(
            line.procurement_id.id,
            procurement_ids[0],
            'Should be the same procurement order id')
