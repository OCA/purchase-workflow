# -*- coding: utf-8 -*-
# Copyright 2015 Alex Comba - Agile Business Group
# Copyright 2017 Tecnativa - vicent.cubells@tecnativa.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo import fields


class TestPurchaseOrderLineDescription(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderLineDescription, cls).setUpClass()
        partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product',
            'standard_price': 10,
            'description_purchase': 'description for purchase',
        })
        group_id = cls.env.ref('purchase_order_line_description.'
                               'group_use_product_description_per_po_line')
        res_users_purchase_user = cls.env.ref('purchase.group_purchase_user')
        cls.test_user = cls.env['res.users'].create(
            {'name': 'test', 'login': 'test',
             'groups_id':
             [(6, 0, [res_users_purchase_user.id])]})
        # add group_use_product_description_per_po_line to test_user
        cls.test_user.write({'groups_id': [(4, group_id.id)]})
        cls.order = cls.env['purchase.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'name': cls.product.name,
                'price_unit': 79.80,
                'product_qty': 15.0,
                'product_uom': cls.env.ref('product.product_uom_unit').id,
                'date_planned': fields.Date.today(),
            })]
        })

    def test_onchange_product_id(self):
        self.assertEqual(self.product.name, self.order.order_line[0].name)
        # Test onchange product
        self.order.order_line[0].sudo(self.test_user).onchange_product_id()
        self.assertEqual(
            self.product.description_purchase, self.order.order_line[0].name)
