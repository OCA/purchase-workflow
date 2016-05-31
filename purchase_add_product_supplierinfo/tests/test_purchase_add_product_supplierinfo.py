# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPurchaseAddProductSupplierinfo(TransactionCase):
    def test_add_product_supplierinfo_from_purchase_order(self):
        # purchase with products to update
        purchase_3 = self.env.ref('purchase.purchase_order_3')
        result = purchase_3.purchase_confirm()
        # open new form when products to update
        self.assertEquals(result['view_type'], 'form')
        self.assertEquals(result['res_model'],
                          'purchase.add.product.supplierinfo')
        self.assertEquals(
            result['context']['default_wizard_line_ids'],
            [(0, 0, {'name': u'D\xe9pannage sur site', 'product_id': 3})])
        self.assertEquals(result['type'], 'ir.actions.act_window')
        self.assertEquals(result['target'], 'new')
        vals = {
            'wizard_line_ids': result['context']['default_wizard_line_ids'],
        }
        wizard = self.env['purchase.add.product.supplierinfo'].create(vals)
        # add product supplierinfo
        wizard.with_context(active_id=purchase_3.id).add_product_supplierinfo()
        supplierinfo_ids = self.env['product.supplierinfo'].search([
            ('product_id', '=',
             result['context']['default_wizard_line_ids'][0][2]['product_id']),
            ('name', '=', purchase_3.partner_id.id)])
        self.assertNotEquals(supplierinfo_ids, False)
