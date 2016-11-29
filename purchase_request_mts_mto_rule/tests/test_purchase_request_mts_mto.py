# -*- coding: utf-8 -*-
# Copyright 2016 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests.common import TransactionCase
from datetime import datetime


class TestPurchaseRequestMtoMts(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestMtoMts, self).setUp()
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.mto_mts_management = True
        self.product = self.env.ref('product.product_product_4')
        self.product.purchase_request = True
        self.company_partner = self.env.ref('base.main_partner')
        self.procurement_obj = self.env['procurement.order']
        self.group = self.env['procurement.group'].create({
            'name': 'test',
        })

        self.quant = self.env['stock.quant'].create({
            'owner_id': self.company_partner.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product.id,
            'qty': 0.0,
        })

    def _procurement_create(self):
        return self.env['procurement.order'].create({
            'location_id': self.env.ref('stock.stock_location_customers').id,
            'product_id': self.product.id,
            'product_qty': 2.0,
            'product_uom': 1,
            'warehouse_id': self.warehouse.id,
            'priority': '1',
            'date_planned': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.product.name,
            'origin': 'test',
            'group_id': self.group.id,
        })

    def test_mts_mto_route_split(self):
        'Create a purchase request with mts+mto rule'
        mto_mts_route = self.env.ref('stock_mts_mto_rule.route_mto_mts')
        buy_route = self.env.ref('purchase.route_warehouse0_buy')
        self.product.route_ids = [(6, 0, [mto_mts_route.id, buy_route.id])]
        self.quant.qty = 1.0
        self._procurement_create()
        purchase_request_lines = self.env['purchase.request.line'].search([])
        self.assertEqual(1, len(purchase_request_lines))
        self.assertEqual(1.0, purchase_request_lines.product_qty)
