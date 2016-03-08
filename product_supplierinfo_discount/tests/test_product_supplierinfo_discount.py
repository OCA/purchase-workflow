# -*- coding: utf-8 -*-
# © 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields


class TestProductSupplierinfoDiscount(common.TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoDiscount, self).setUp()
        self.po_model = self.env['purchase.order.line']
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_6')
        self.supplierinfo = self.supplierinfo_model.create({
            'min_qty': 0.0,
            'name': self.partner_3.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'discount': 10,
        })
        self.supplierinfo2 = self.supplierinfo_model.create({
            'min_qty': 10.0,
            'name': self.partner_3.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'discount': 20,
        })
        self.purchase_order = self.env['purchase.order'].create(
            {'partner_id': self.partner_3.id})
        self.po_line_1 = self.po_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1.0,
             'product_uom': self.env.ref('product.product_uom_categ_unit').id,
             'price_unit': 10.0})

    def test_001_purchase_order_partner_3_qty_1(self):
        self.po_line_1._onchange_quantity()
        self.assertEquals(
            self.po_line_1.discount, 10,
            "Incorrect discount for product 6 with partner 3 and qty 1: "
            "Should be 10%")

    def test_002_purchase_order_partner_3_qty_10(self):
        self.po_line_1.write({'product_qty': 10})
        self.po_line_1._onchange_quantity()
        self.assertEquals(
            self.po_line_1.discount, 20.0,
            "Incorrect discount for product 6 with partner 3 and qty 10: "
            "Should be 20%")

    def test_003_purchase_order_partner_1_qty_1(self):
        self.po_line_1.write({
            'partner_id': self.partner_1.id,
            'product_qty': 1,
        })
        self.po_line_1.onchange_product_id()
        self.assertEquals(
            self.po_line_1.discount, 0.0, "Incorrect discount for product "
            "6 with partner 1 and qty 1")
