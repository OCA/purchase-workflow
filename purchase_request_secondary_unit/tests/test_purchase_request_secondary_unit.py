# Copyright 2020 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestPurchaseRequestSecondaryUnit(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref('uom.product_uom_kgm')
        cls.product_uom_gram = cls.env.ref('uom.product_uom_gram')
        cls.product_uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'uom_id': cls.product_uom_kg.id,
            'uom_po_id': cls.product_uom_kg.id,
            'secondary_uom_ids': [
                (0, 0, {
                    'name': 'unit-700',
                    'uom_id': cls.product_uom_unit.id,
                    'factor': 0.7,
                })],
        })
        cls.secondary_unit = cls.env['product.secondary.unit'].search([
            ('product_tmpl_id', '=', cls.product.product_tmpl_id.id),
        ])
        cls.product.purchase_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env['res.partner'].create({
            'name': 'test - partner',
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
        cls.purchase_request_obj = cls.env['purchase.request']
        pr_val = {
            'company_id': cls.env.user.company_id.id,
            'picking_type_id': picking_type_id.id,
            'line_ids': [(0, 0, {
                'name': cls.product.name,
                'product_id': cls.product.id,
                'product_qty': 1,
                'product_uom_id': cls.product.uom_id.id,
            })],
        }
        cls.request = cls.purchase_request_obj.create(pr_val)
        cls.wiz_obj =\
            cls.env['purchase.request.line.make.purchase.order']

    def test_onchange_secondary_uom(self):
        self.request.line_ids.write({
            'secondary_uom_id': self.secondary_unit.id,
            'secondary_uom_qty': 5,
        })
        self.request.line_ids._onchange_secondary_uom_id()
        self.assertEqual(
            self.request.line_ids.product_qty, 3.5)

    def test_onchange_product_qty_purchase_request_secondary_unit(self):
        self.request.line_ids.update({
            'secondary_uom_id': self.secondary_unit.id,
            'product_qty': 3.5,
        })
        self.request.line_ids.\
            _onchange_product_qty_purchase_request_secondary_unit()
        self.assertEqual(
            self.request.line_ids.secondary_uom_qty, 5.0)

    def test_default_secondary_unit(self):
        self.request.line_ids.\
            _onchange_product_id_purchase_request_secondary_unit()
        self.assertEqual(
            self.request.line_ids.secondary_uom_id, self.secondary_unit)

    def test_onchange_request_product_uom(self):
        self.request.line_ids.update({
            'secondary_uom_id': self.secondary_unit.id,
            'product_uom_id': self.product_uom_gram.id,
            'product_qty': 3500.00,
        })
        self.request.line_ids.\
            _onchange_product_uom_id_purchase_request_secondary_unit()
        self.assertEqual(
            self.request.line_ids.secondary_uom_qty, 5.0)

    def test_wizard_create_po_propagate_secondary_unit(self):
        self.request.line_ids.write({
            'secondary_uom_id': self.secondary_unit.id,
            'secondary_uom_qty': 5,
            'product_qty': 3.5,
        })
        self.request.button_to_approve()
        self.request.button_approved()
        vals = {
            'supplier_id': self.env.ref('base.res_partner_12').id,
        }
        wiz = self.wiz_obj.with_context(
            active_model="purchase.request.line",
            active_ids=self.request.line_ids.ids).create(vals)
        self.assertEqual(wiz.item_ids.secondary_uom_qty, 5)
        self.assertEqual(
            wiz.item_ids.secondary_uom_id.id, self.secondary_unit.id)
        wiz.make_purchase_order()
        po_line = self.request.line_ids.purchase_lines
        self.assertEqual(po_line.secondary_uom_qty, 5)
        self.assertEqual(po_line.secondary_uom_id.id, self.secondary_unit.id)
