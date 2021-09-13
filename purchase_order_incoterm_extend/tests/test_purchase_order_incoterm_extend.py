# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseOrderIncotermExtend(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref('uom.product_uom_kgm')
        cls.product_uom_gram = cls.env.ref('uom.product_uom_gram')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'test-partner',
            'supplier': True,
        })
        type_obj = cls.env['stock.picking.type']
        company_id = cls.env.user.company_id.id
        picking_type_id = type_obj.search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', company_id)
        ], limit=1)
        if not picking_type_id:
            picking_type_id = cls.env.ref('stock.picking_type_in')
        cls.purchase_order_obj = cls.env['purchase.order']
        po_val = {
            'partner_id': cls.partner.id,
            'company_id': cls.env.user.company_id.id,
            'picking_type_id': picking_type_id.id,
            'order_line': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_qty': 1,
                'product_uom': cls.product.uom_id.id,
                'price_unit': 1000.00,
                'date_planned': fields.Datetime.now(),
                'incoterm_place': 'TestSentence',
            })],
        }
        po = cls.purchase_order_obj.new(po_val)
        po.onchange_partner_id()
        cls.order = cls.purchase_order_obj.create(po_val)

    def test_01_onchange_incoterm_place(self):
        self.assertTrue(self.order, 'Purchase: no purchase order created')

    def test_02_incoterm_place_allow_empty(self):
        self.order.update({'incoterm_place': ''})
        self.assertTrue(self.order, 'Purchase: no purchase order created')

    def test_03_incoterm_place_able_to_update(self):
        self.order.update({'incoterm_place': 'TestSentence2'})
        self.assertTrue(self.order, 'Purchase: no purchase order created')

    def test_04_incoterm_place_able_to_contain_zenkaku_char(self):
        self.order.update({'incoterm_place': 'テスト　（全角スペース）文章'})
        self.assertTrue(self.order, 'Purchase: no purchase order created')
