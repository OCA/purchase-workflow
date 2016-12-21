# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common
from openerp import fields


class TestPurchaseOrderType(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderType, cls).setUpClass()
        cls.incoterm = cls.env['stock.incoterms'].create({
            'name': 'Test incoterm',
            'code': 'TEST',
        })
        cls.picking_type = cls.env['stock.picking.type'].create({
            'name': 'Test',
            'code': 'internal',
            'sequence_id': cls.env['ir.sequence'].create({
                'name': 'Test sequence',
                'code': 'TEST',
            }).id,
        })
        cls.order_type = cls.env['purchase.order.type'].create({
            'name': 'Test type',
            'incoterm_id': cls.incoterm.id,
            'picking_type_id': cls.picking_type.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'purchase_type': cls.order_type.id,
        })
        cls.order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'date_planned': fields.Date.today(),
        })

    def test_onchange_partner(self):
        self.order.onchange_partner_id_purchase_order_type()
        self.assertEqual(self.order.order_type, self.order_type)

    def test_onchange_order_type(self):
        self.order.order_type = self.order_type
        self.order.onchange_purchase_order_type()
        self.assertEqual(self.order.incoterm_id, self.incoterm)
        self.assertEqual(self.order.picking_type_id, self.picking_type)
