# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestPurchaseAddProductSupplierinfo(TransactionCase):
    def test_add_product_supplierinfo_on_product_template(self):
        # purchases with product supplierinfo to update and
        # product supplierinfo is on product_template
        purchase_8 = self.env.ref(
            'purchase_add_product_supplierinfo.purchase_order_8')
        result8 = purchase_8.purchase_confirm()
        # open new form when products to update
        self.assertEquals(result8['view_mode'], 'form')
        self.assertEquals(result8['res_model'],
                          'purchase.add.product.supplierinfo')
        self.assertEquals(
            result8['context']['default_wizard_line_ids'],
            [(0, 0, {
                'to_variant': True,
                'name': u'iPad Retina Display',
                'product_id': 6
            })])
        self.assertEquals(result8['type'], 'ir.actions.act_window')
        self.assertEquals(result8['target'], 'new')
        vals = {
            'wizard_line_ids': result8['context']['default_wizard_line_ids'],
        }
        vals['wizard_line_ids'][0][2]['to_variant'] = False
        wizard = self.env['purchase.add.product.supplierinfo'].create(vals)
        # add product supplierinfo
        wizard.with_context(active_id=purchase_8.id).add_product_supplierinfo()
        product = self.env['product.product'].browse(
            result8['context']['default_wizard_line_ids'][0][2]['product_id'])
        supplierinfo_ids = self.env['product.supplierinfo'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('name', '=', purchase_8.partner_id.id)])
        self.assertNotEquals(supplierinfo_ids, False)

    def test_add_product_supplierinfo_on_product_product(self):
        # purchases with product supplierinfo to update and
        # product supplierinfo is on product_product
        purchase_9 = self.env.ref(
            'purchase_add_product_supplierinfo.purchase_order_9')
        result9 = purchase_9.purchase_confirm()
        # open new form when products to update
        self.assertEquals(result9['view_mode'], 'form')
        self.assertEquals(result9['res_model'],
                          'purchase.add.product.supplierinfo')
        self.assertEquals(
            result9['context']['default_wizard_line_ids'],
            [(0, 0, {
                'to_variant': True,
                'name': u'iMac',
                'product_id': 13
            })])
        self.assertEquals(result9['type'], 'ir.actions.act_window')
        self.assertEquals(result9['target'], 'new')
        vals = {
            'wizard_line_ids': result9['context']['default_wizard_line_ids'],
        }
        wizard = self.env['purchase.add.product.supplierinfo'].create(vals)
        # add product supplierinfo
        wizard.with_context(active_id=purchase_9.id).add_product_supplierinfo()
        supplierinfo_ids = self.env['product.supplierinfo'].search([
            ('product_id', '=',
             result9['context']['default_wizard_line_ids'][0][2]
             ['product_id']),
            ('name', '=', purchase_9.partner_id.id)])
        self.assertNotEquals(supplierinfo_ids, False)

    def test_without_add_product_supplierinfo(self):
        # purchases without product supplierinfo to update
        purchase_11 = self.env.ref(
            'purchase_add_product_supplierinfo.purchase_order_11')
        result11 = purchase_11.purchase_confirm()
        self.assertEquals(result11, None)
