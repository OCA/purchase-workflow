# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPurchaseAddProductSupplierinfo(TransactionCase):
    def test_add_product_supplierinfo_from_purchase_order(self):
        #suppliers = self.env['res.partner'].search([
        #    ('supplier', '=', True),
        #    ('active', '=', True),
        #])
        products = self.env['product.product'].search([
            ('seller_ids', '=', False),
            ('purchase_ok', '=', True),
            ('active', '=', True),
        ])
        if products:
            order_lines = self.env['purchase.order.line'].search([
                ('state', '=', 'draft'),
                ('product_id', 'in', products.ids),
            ])
        if order_lines:
            order = order_lines[0].order_id
