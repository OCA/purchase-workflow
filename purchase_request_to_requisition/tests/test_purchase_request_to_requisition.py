# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common
from openerp.tools import SUPERUSER_ID


class TestPurchaseRequestToRequisition(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestToRequisition, self).setUp()
        self.purchase_request = self.env['purchase.request']
        self.purchase_request_line = self.env['purchase.request.line']
        self.wiz =\
            self.env['purchase.request.line.make.purchase.requisition']
        self.purchase_requisition_partner_model =\
            self.env['purchase.requisition.partner']
        self.purchase_order = self.env['purchase.order']

    def test_purchase_request_to_purchase_requisition(self):
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
        purchase_request_line = self.purchase_request_line.create(vals)
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line.id],
            active_id=purchase_request_line.id,).create({})
        wiz_id.make_purchase_requisition()
        self.assertTrue(
            len(purchase_request_line.requisition_lines.ids) == 1,
            'Should have one purchase requisition line created')
        requisition_id = purchase_request_line.requisition_lines.requisition_id
        self.assertEquals(
            len(purchase_request.line_ids),
            len(requisition_id.line_ids), 'Should have the same lines')
        requisition_line = requisition_id.line_ids
        self.assertEquals(
            requisition_line.product_id.id,
            purchase_request_line.product_id.id,
            'Should have the same products')
        self.assertEquals(
            purchase_request.state,
            requisition_id.state,
            'Should have the same state')
        requisition_id.tender_in_progress()
        requisition_id.tender_open()
        vals = {
            'partner_id': self.env.ref('base.res_partner_12').id,
        }
        requisition_partner_id =\
            self.purchase_requisition_partner_model.with_context(
                active_model='purchase.requisition',
                active_ids=[requisition_id.id],
                active_id=requisition_id.id,).create(vals)
        requisition_partner_id.create_order()
        domain = [
            ('requisition_id', '=', requisition_id.id),
        ]
        purchase_id = self.purchase_order.search(domain)
        self.assertTrue(purchase_id, 'Should find purchase order')
        purchase_id.signal_workflow('purchase_confirm')
        self.assertEquals(
            len(
                purchase_id.order_line.purchase_request_lines
            ), 1, 'Should have a link between order lines and request lines')
