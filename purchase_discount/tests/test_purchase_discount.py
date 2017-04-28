# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp import fields


class TestPurchaseOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.product_1 = cls.env['product.product'].create({
            'name': 'Test product 1',
            'type': 'product',
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Test product 2',
            'type': 'product',
        })
        po_model = cls.env['purchase.order.line']
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test supplier',
            'supplier': True,
        })
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
        })
        cls.po_line_1 = po_model.create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product_1.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': cls.product_1.uom_id.id,
            'discount': 50.0,
            'price_unit': 10.0,
        })
        cls.tax = cls.env['account.tax'].create({
            'name': 'Sample tax 15%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 15.0,
        })
        cls.po_line_2 = po_model.create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product_2.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 10.0,
            'product_uom': cls.product_2.uom_id.id,
            'discount': 30,
            'taxes_id': [(6, 0, cls.tax.ids)],
            'price_unit': 230.0,
        })

    def test_purchase_order_vals(self):
        self.assertEqual(self.po_line_1.price_subtotal, 5.0)
        self.assertEqual(self.po_line_2.price_subtotal, 1610.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1615.0)
        self.assertEqual(self.purchase_order.amount_tax, 241.5)

    def test_move_price_unit(self):
        self.purchase_order.button_confirm()
        self.assertEqual(self.po_line_1.move_ids[0].price_unit, 5.0)
        self.assertEqual(self.po_line_2.move_ids[0].price_unit, 161.0)
