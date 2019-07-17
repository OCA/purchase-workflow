# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common
from odoo.tools import SUPERUSER_ID


class TestPurchaseRequestToRfq(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz =\
            self.env['purchase.request.line.make.purchase.order']
        self.purchase_order = self.env['purchase.order']
        vendor = self.env['res.partner'].create({
            'name': 'Partner #2',
        })
        supplierinfo_service = self.env['product.supplierinfo'].create({
            'name': vendor.id,
        })
        supplierinfo_product = self.env['product.supplierinfo'].create({
            'name': vendor.id,
        })
        self.service_product = self.env['product.product'].create({
            'name': 'Product Service Test',
            'seller_ids': [(6, 0, [supplierinfo_service.id])],
            'type': 'service',
            'service_to_purchase': True,
        })
        self.product_product = self.env['product.product'].create({
            'name': 'Product Product Test',
            'seller_ids': [(6, 0, [supplierinfo_product.id])],
            'type': 'product'
        })

    def test_purchase_request_allocation(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request1.id,
            'product_id': self.product_product.id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_qty': 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            'supplier_id': self.env.ref('base.res_partner_1').id,
        }
        purchase_request1.button_approved()
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request2.id,
            'product_id': self.product_product.id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_qty': 2.0,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        vals = {
            'supplier_id': self.env.ref('base.res_partner_1').id,
        }
        purchase_request1.button_approved()
        purchase_request2.button_approved()

        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id,
                        purchase_request_line2.id]).create(vals)
        wiz_id.make_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        purchase = po_line.order_id
        purchase.button_confirm()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        self.assertEqual(purchase_request_line2.qty_in_progress, 2.0)
        picking = purchase.picking_ids[0]
        picking.move_line_ids[0].write({'qty_done': 2.0})
        backorder_wiz_id = picking.button_validate()['res_id']
        backorder_wiz = self.env['stock.backorder.confirmation'].browse(
            [backorder_wiz_id])
        backorder_wiz.process()
        self.assertEqual(purchase_request_line1.qty_done, 2.0)
        self.assertEqual(purchase_request_line2.qty_done, 0.0)

        backorder_picking = purchase.picking_ids.filtered(
            lambda p: p.id != picking.id)
        backorder_picking.move_line_ids[0].write({'qty_done': 1.0})
        backorder_wiz_id2 = backorder_picking.button_validate()['res_id']
        backorder_wiz2 = self.env['stock.backorder.confirmation'].browse(
            [backorder_wiz_id2])
        backorder_wiz2.process()

        self.assertEqual(purchase_request_line1.qty_done, 2.0)
        self.assertEqual(purchase_request_line2.qty_done, 1.0)
        purchase.picking_ids[0].action_cancel()
        self.assertEqual(purchase_request_line1.qty_cancelled, 0.0)
        self.assertEqual(purchase_request_line2.qty_cancelled, 1.0)

    def test_purchase_request_allocation_services(self):
        vals = {
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request1.id,
            'product_id': self.service_product.id,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'product_qty': 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            'supplier_id': self.env.ref('base.res_partner_1').id,
        }
        purchase_request1.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id]).create(vals)
        wiz_id.make_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        purchase = po_line.order_id
        purchase.button_confirm()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        # manually set in the PO line
        po_line.write({'qty_received': 0.5})
        self.assertEqual(purchase_request_line1.qty_done, 0.5)
        purchase.button_cancel()
        self.assertEqual(purchase_request_line1.qty_cancelled, 1.5)
