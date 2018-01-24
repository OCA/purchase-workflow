# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo import fields
from odoo.exceptions import UserError


class TestPurchaseRequestProcurement(common.SavepointCase):

    def setUp(self):
        super(TestPurchaseRequestProcurement, self).setUp()
        self.pr_model = self.env['purchase.request']
        self.prl_model = self.env['purchase.request.line']
        self.product_uom_model = self.env['product.uom']

        self.uom_unit_categ = self.env.ref('product.product_uom_categ_unit')

        self.product_1 = self.env.ref('product.product_product_16')
        self.product_1.purchase_request = True
        self.product_2 = self.env.ref('product.product_product_13')

        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_ten = self.product_uom_model.create({
            'name': "Ten",
            'category_id': self.uom_unit_categ.id,
            'factor_inv': 10,
            'uom_type': 'bigger',
        })

    def create_procurement_order(self, name, product, qty):
        values = {
            'name': name,
            'date_planned': fields.Datetime.now(),
            'product_id': product.id,
            'product_qty': qty,
            'product_uom': product.uom_id.id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'route_ids': [
                (4, self.env.ref('purchase.route_warehouse0_buy').id, 0)],
            'company_id': self.env.ref('base.main_company').id,
        }
        return self.env['procurement.order'].create(values)

    def test_cancel_purchase_request(self):
        """Test if when a PR is cancelled, the linked procurements that
        are not yet cancelled become cancelled."""
        proc = self.create_procurement_order('TEST/0001', self.product_1, 4)
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
        proc = self.create_procurement_order('TEST/0002', self.product_1, 4)
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
        proc = self.create_procurement_order('TEST/0003', self.product_1, 4)
        request = proc.request_id
        proc.write({'state': 'done'})
        with self.assertRaises(UserError):
            request.button_rejected()
        with self.assertRaises(UserError):
            request.button_draft()

    def test_product_uom_po_id(self):
        product = self.product_1
        product.write({
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_ten.id,
        })
        proc = self.create_procurement_order('TEST/0004', self.product_1, 100)
        request = proc.request_id
        line = request.line_ids[0]
        self.assertEqual(line.product_uom_id, self.uom_ten)
        self.assertEqual(line.product_qty, 10)
