# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase
from odoo.tools import SUPERUSER_ID


class TestPurchaseRequestToRequisition(SavepointCase):

    def setUp(cls):
        super(TestPurchaseRequestToRequisition, cls).setUp()

        # MODELS
        cls.purchase_request = cls.env['purchase.request']
        cls.purchase_request_line = cls.env['purchase.request.line']
        cls.wiz = \
            cls.env['purchase.request.line.make.purchase.requisition']
        cls.purchase_order = cls.env['purchase.order']

        # INSTANCES
        cls.pycking_type = cls.env.ref('stock.picking_type_in')
        cls.product = cls.env.ref('product.product_product_13')
        cls.product_uom = cls.env.ref('product.product_uom_unit')
        cls.partner = cls.env.ref('base.res_partner_12')

    def test_purchase_request_to_purchase_requisition(self):
        vals = {
            'picking_type_id': self.pycking_type.id,
            'requested_by': SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            'request_id': purchase_request.id,
            'product_id': self.product.id,
            'product_uom_id': self.product_uom.id,
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
        requisition_id.action_in_progress()
        requisition_id.action_open()
        vals = {
            'partner_id': self.partner.id,
            'requisition_id': requisition_id.id
        }
        po = self.purchase_order.create(vals)
        po._onchange_requisition_id()
        domain = [
            ('requisition_id', '=', requisition_id.id),
        ]
        purchase_id = self.purchase_order.search(domain)
        # because travis install all repo (purchase_fop_shipping)
        # may be an edge effect
        if 'force_order_under_fop' in purchase_id._fields:
            purchase_id.force_order_under_fop = True
        self.assertTrue(purchase_id, 'Should find purchase order')
        # fail : not po.force_order_under_fop and not po.fop_reached
        purchase_id.button_confirm()
        self.assertEquals(purchase_id.order_line.product_id.id,
                          purchase_id.requisition_id.line_ids.product_id.id,
                          'Should have same product between order lines and '
                          'request lines')
        self.assertEquals(
            len(
                purchase_id.order_line
            ),
            len(purchase_id.requisition_id.line_ids),
            'Should have a link between order lines and request lines')
