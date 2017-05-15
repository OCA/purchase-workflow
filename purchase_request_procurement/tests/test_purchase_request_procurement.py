# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp.tests import common
from openerp import fields
from openerp.exceptions import UserError


class TestPurchaseRequestProcurement(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestProcurement, self).setUp()
        self.pr_model = self.env['purchase.request']
        self.prl_model = self.env['purchase.request.line']
        self.product_1 = self.env.ref('product.product_product_16')
        self.product_1.purchase_request = True
        self.product_2 = self.env.ref('product.product_product_13')

    def create_purchase_request(self, name):
        values = {
            'name': name,
            'date_planned': fields.Datetime.now(),
            'product_id': self.product_1.id,
            'product_qty': 4.0,
            'product_uom': self.product_1.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (4, self.env.ref('purchase.route_warehouse0_buy').id, 0)],
        }
        return self.env['procurement.order'].create(values)

    def test_cancel_purchase_request(self):
        """Test if when a PR is cancelled, the linked procurements that
        are not yet cancelled become cancelled."""
        proc = self.create_purchase_request('TEST/0001')
        proc.run()
        request = proc.request_id
        self.assertFalse(request.line_ids[0].cancelled)
        self.assertEqual(
            proc.id, request.line_ids[0].procurement_id.id,
            "Procurement in Purchase Request line is not matching.")
        request.button_rejected()
        self.assertTrue(request.line_ids[0].cancelled)
        self.assertFalse(
            proc.request_id,
            "Procurement's Purchase Request must have been empty after "
            "rejecting the PR.")

    def test_cancel_procurement(self):
        """Tests if the PR lines that are linked to a procurement are
        cancelled when a procurement is cancelled."""
        proc = self.create_purchase_request('TEST/0002')
        proc.run()
        pr_line = proc.request_id.line_ids[0]
        self.assertFalse(pr_line.cancelled)
        proc.cancel()
        self.assertTrue(
            pr_line.cancelled,
            "Purchase Request line hasn't been cancelled with its "
            "procurement.")

    def test_cancel_line_with_done_procurement(self):
        """Tests that it isn't allowed to cancel or reset a PR with lines
        realted to done procurements."""
        proc = self.create_purchase_request('TEST/0003')
        request = proc.request_id
        proc.write({'state': 'done'})
        with self.assertRaises(UserError):
            request.button_rejected()
        with self.assertRaises(UserError):
            request.button_draft()
