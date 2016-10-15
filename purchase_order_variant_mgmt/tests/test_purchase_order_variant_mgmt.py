# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestPurchaseOrderVariantMgmt(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderVariantMgmt, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.attribute1 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 1',
            'value_ids': [
                (0, 0, {'name': 'Value 1'}),
                (0, 0, {'name': 'Value 2'}),
            ],
        })
        cls.attribute2 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 2',
            'value_ids': [
                (0, 0, {'name': 'Value X'}),
                (0, 0, {'name': 'Value Y'}),
            ],
        })
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'Test template',
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': cls.attribute1.id,
                    'value_ids': [(6, 0, cls.attribute1.value_ids.ids)],
                }),
                (0, 0, {
                    'attribute_id': cls.attribute2.id,
                    'value_ids': [(6, 0, cls.attribute2.value_ids.ids)],
                }),
            ],
        })
        assert len(cls.product_tmpl.product_variant_ids) == 4
        order = cls.env['purchase.order'].new({'partner_id': cls.partner.id})
        order.onchange_partner_id()
        cls.order = order.create(order._convert_to_write(order._cache))
        cls.Wizard = cls.env['purchase.manage.variant'].with_context(
            active_ids=cls.order.ids, active_id=cls.order.id,
            active_model=cls.order._name
        )
        cls.PurchaseOrderLine = cls.env['purchase.order.line']

    def test_add_variants(self):
        wizard = self.Wizard.new({'product_tmpl_id': self.product_tmpl.id})
        wizard._onchange_product_tmpl_id()
        wizard = wizard.create(wizard._convert_to_write(wizard._cache))
        self.assertEqual(len(wizard.variant_line_ids), 4)
        wizard.variant_line_ids[0].product_uom_qty = 1
        wizard.variant_line_ids[1].product_uom_qty = 2
        wizard.variant_line_ids[2].product_uom_qty = 3
        wizard.variant_line_ids[3].product_uom_qty = 4
        wizard.button_transfer_to_order()
        self.assertEqual(len(self.order.order_line), 4,
                         "There should be 4 lines in the sale order")

    def test_modify_variants(self):
        product1 = self.product_tmpl.product_variant_ids[0]
        order_line1 = self.PurchaseOrderLine.new({
            'order_id': self.order.id,
            'product_id': product1.id,
        })
        order_line1.onchange_product_id()
        order_line1.product_qty = 1
        order_line1._onchange_quantity()
        product2 = self.product_tmpl.product_variant_ids[1]
        order_line1 = self.PurchaseOrderLine.create(
            order_line1._convert_to_write(order_line1._cache))
        order_line2 = self.PurchaseOrderLine.new({
            'order_id': self.order.id,
            'product_id': product2.id,
        })
        order_line2.onchange_product_id()
        order_line1.product_qty = 2
        order_line2._onchange_quantity()
        order_line2 = self.PurchaseOrderLine.create(
            order_line2._convert_to_write(order_line2._cache))
        Wizard2 = self.Wizard.with_context(
            default_product_tmpl_id=self.product_tmpl.id,
            active_model='purchase.order.line',
            active_id=order_line1.id, active_ids=order_line1.ids
        )
        wizard = Wizard2.create({})
        wizard._onchange_product_tmpl_id()
        self.assertEqual(
            len(wizard.variant_line_ids.filtered('product_uom_qty')), 2,
            "There should be two fields with any quantity in the wizard."
        )
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == product1).product_uom_qty = 0
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == product2).product_uom_qty = 10
        wizard.button_transfer_to_order()
        self.assertFalse(order_line1.exists(), "Order line not removed.")
        self.assertEqual(
            order_line2.product_qty, 10, "Order line quantity not changed.")
