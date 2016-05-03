# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPurchaseAddProductSupplierinfo(TransactionCase):
    def test_add_product_supplierinfo_from_purchase_order(self):
        # purchase without products to update
        purchase_4 = self.env.ref('purchase.purchase_order_4')
        result = purchase_4.purchase_confirm()
        # only confirm purchase order when not products to update
        self.assertEquals(result, None)
        # purchase with products to update
        purchase_7 = self.env.ref('purchase.purchase_order_7')
        result = purchase_7.purchase_confirm()
        # open new form when products to update
        self.assertEquals(result['view_type'], 'form')
        self.assertEquals(result['res_model'],
                          'purchase.add.product.supplierinfo')
        self.assertEquals(result['context']['default_product_ids'][0][2],
                          [18, 40])
        self.assertEquals(result['type'], 'ir.actions.act_window')
        self.assertEquals(result['target'], 'new')
        vals = {'product_ids': result['context']['default_product_ids']}
        wizard = self.env['purchase.add.product.supplierinfo'].create(vals)
        # add product supplierinfo
        wizard.with_context(active_id=purchase_7.id).add_product_supplierinfo()
        supplierinfo_ids = self.env['product.supplierinfo'].search([
            ('product_id', 'in',
             result['context']['default_product_ids'][0][2]),
            ('name', '=', purchase_7.partner_id.id)])
        self.assertNotEquals(supplierinfo_ids, False)
