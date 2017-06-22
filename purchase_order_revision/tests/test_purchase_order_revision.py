# -*- coding: utf-8 -*-
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo import fields


class TestPurchaseOrderRevision(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderRevision, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test',
        })
        cls.order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'date_planned': fields.Date.today(),
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'name': cls.product.name,
                'price_unit': 79.80,
                'product_qty': 15.0,
                'product_uom': cls.env.ref('product.product_uom_unit').id,
                'date_planned': fields.Date.today(),
            })]
        })

    def test_new_revision(self):
        # I cancel the PO and create a new revision
        self.order.button_cancel()
        self.assertEqual(self.order.state, 'cancel')
        old_name = self.order.name
        new_name = '%s-01' % old_name
        self.order.new_revision()
        self.assertEqual(self.order.name, new_name)
        self.assertEqual(len(self.order.old_revision_ids), 1)
        self.assertEqual(self.order.revision_number, 1)
        old_order = self.env['purchase.order'].search([
            ('name', '=', old_name),
        ])
        self.assertEqual(old_order.active, False)
