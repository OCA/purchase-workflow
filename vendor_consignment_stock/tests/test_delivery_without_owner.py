# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestDeliveryWithoutOwner(TransactionCase):

    def test_it_still_fully_reserves_my_stock(self):
        self.own_quant.qty = 12
        self.vendor_quant.qty = 100
        self.move.product_uom_qty = 10

        self.picking.action_assign()
        self.assertEqual('assigned', self.picking.state)

    def setUp(self):
        super(TestDeliveryWithoutOwner, self).setUp()
        self.product = self.env.ref('product.product_product_6')
        vendor = self.env.ref('base.res_partner_1')
        self.own_quant = self.env['stock.quant'].create({
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
            'qty': 0.0,
        })
        self.vendor_quant = self.env['stock.quant'].create({
            'owner_id': vendor.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
            'qty': 0.0,
        })
        self.picking = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
        })
        self.move = self.env['stock.move'].create({
            'name': '/',
            'picking_id': self.picking.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id':
            self.env.ref('stock.stock_location_customers').id,
            'product_id': self.product.id,
        })
