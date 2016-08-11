# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests import common
from openerp import fields
from openerp.exceptions import ValidationError


class TestPurchaseRequestProcurement(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestProcurement, self).setUp()
        self.purchase_request_ = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.product_1 = self.env.ref('product.product_product_16')
        self.product_1.purchase_request = True
        self.product_2 = self.env.ref('product.product_product_13')

    def create_purchase_request(self, name):
        values = {'company_id': self.env.ref('base.main_company').id,
                  'date_planned': fields.Datetime.now(),
                  'name': name,
                  'product_id': self.product_1.id,
                  'product_qty': 4,
                  'product_uom': self.product_1.uom_id.id,
                  'warehouse_id': self.env.ref('stock.warehouse0').id,
                  'location_id': self.env.ref('stock.stock_location_stock').id,
                  'route_ids':
                      [(
                       4, self.env.ref('purchase.route_warehouse0_buy').id,
                       0)],
                  }

        return self.env['procurement.order'].create(values)

    def test_1_purchase_request_in_progress(self):

        proc = self.create_purchase_request('SOME/TEST/0001')
        proc.check()
        proc.run()
        request = proc.request_id
        request.button_approved()
        with self.assertRaises(ValidationError):
            proc.cancel()

    def test_2_purchase_request_remove_lines(self):
        proc = self.create_purchase_request('SOME/TEST/0002')
        proc.check()
        proc.run()
        request = proc.request_id
        self.assertEqual(len(request.line_ids), 1)
        proc.cancel()
        request = proc.request_id
        self.assertEqual(len(request), 0)

    def test_3_purchase_request_keep_manual(self):
        proc = self.create_purchase_request('SOME/TEST/0003')
        proc.check()
        proc.run()
        request = proc.request_id
        # create line
        vals = {
            'request_id': request.id,
            'product_id': self.product_2.id,
            'product_uom_id': self.product_2.uom_id.id,
            'product_qty': 5.0,
        }
        self.purchase_request_line.create(vals)
        self.assertEqual(len(request.line_ids), 2)
        proc.cancel()
        self.assertEqual(len(request.line_ids), 1)
