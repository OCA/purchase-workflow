# -*- coding: utf-8 -*-
# © 2015 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestPurchaseOrderLineDescription(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderLineDescription, self).setUp()
        self.res_users_model = self.env['res.users']
        self.res_partner_model = self.env['res.partner']
        self.product_model = self.env['product.product']
        self.po_line_model = self.env['purchase.order.line']
        self.partner = self.env.ref('base.res_partner_1')
        self.pricelist_model = self.env['product.pricelist']

        group_id = self.ref('purchase_order_line_description.'
                            'group_use_product_description_per_po_line')

        self.test_user = self.res_users_model.create(
            {'name': 'test', 'login': 'test',
             'groups_id':
             [(6, 0, [self.ref('purchase.group_purchase_user')])]})
        # add group_use_product_description_per_po_line to test_user
        self.test_user.write({'groups_id': [(4, group_id)]})

        self.product = self.product_model.create({
            'name': 'Product',
            'standard_price': 10,
            'description_purchase': 'description for purchase',
        })

    def test_onchange_product_id(self):
        pricelist = self.pricelist_model.search(
            [('name', '=', 'Public Pricelist')])[0]
        uom_id = self.env.ref('product.product_uom_categ_unit')
        res = self.po_line_model.sudo(self.test_user).onchange_product_id(
            pricelist.id, self.product.id, 10, uom_id.id, self.partner.id)
        self.assertEqual(
            self.product.description_purchase, res['value']['name'])
