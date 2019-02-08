# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo.tests import common
from odoo import fields
from odoo.exceptions import UserError


class TestPurchaseBlanketOrders(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseBlanketOrders, self).setUp()
        self.blanket_order_obj = self.env['purchase.blanket.order']
        self.blanket_order_line_obj = self.env['purchase.blanket.order.line']
        self.blanket_order_wiz_obj = self.env['purchase.blanket.order.wizard']

        self.partner = self.env['res.partner'].create({
            'name': 'TEST SUPPLIER',
            'supplier': True,
        })
        self.payment_term = self.env.ref('account.account_payment_term_net')

        # Seller IDS
        seller = self.env['product.supplierinfo'].create({
            'name': self.partner.id,
            'price': 30.0,
        })

        self.product = self.env['product.product'].create({
            'name': 'Demo',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 35.0,
            'seller_ids': [(6, 0, [seller.id])],
            'type': 'consu',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PROD_DEL01',
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Demo 2',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 50.0,
            'type': 'consu',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PROD_DEL02',
        })

        self.yesterday = date.today() - timedelta(days=1)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_create_blanket_order(self):
        """ We create a blanket order and check constrains to confirm BO """
        blanket_order = self.blanket_order_obj.create({
            'partner_id': self.partner.id,
            'validity_date': fields.Date.to_string(self.yesterday),
            'payment_term_id': self.payment_term.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'original_qty': 20.0,
                'price_unit': 0.0,  # will be updated later
            })],
        })
        blanket_order.onchange_partner_id()
        blanket_order.line_ids[0].onchange_product()

        self.assertEqual(blanket_order.state, 'draft')
        self.assertEqual(blanket_order.line_ids[0].price_unit, 30.0)

        # date in the past
        with self.assertRaises(UserError):
            blanket_order.action_confirm()

        blanket_order.validity_date = fields.Date.to_string(self.tomorrow)
        blanket_order.action_confirm()

        self.assertEqual(blanket_order.state, 'open')

    def test_create_purchase_orders_from_blanket_order(self):
        """ We create a blanket order and create two purchase orders """
        blanket_order = self.blanket_order_obj.create({
            'partner_id': self.partner.id,
            'validity_date': fields.Date.to_string(self.tomorrow),
            'payment_term_id': self.payment_term.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'original_qty': 20.0,
                'price_unit': 30.0,
            })],
        })
        blanket_order.onchange_partner_id()
        blanket_order.action_confirm()

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id,
            active_model='purchase.blanket.order').create({})
        wizard1.line_ids[0].write({'qty': 10.0})
        wizard1.create_purchase_order()

        wizard2 = self.blanket_order_wiz_obj.with_context(
            active_id=blanket_order.id,
            active_model='purchase.blanket.order').create({})
        wizard2.line_ids[0].write({'qty': 10.0})
        wizard2.create_purchase_order()

        self.assertEqual(blanket_order.state, 'done')

        self.assertEqual(blanket_order.purchase_count, 2)

        view_action = blanket_order.action_view_purchase_orders()
        domain_ids = view_action['domain'][0][2]
        self.assertEqual(len(domain_ids), 2)

    def test_create_purchase_orders_from_blanket_order_line(self):
        """ We create a blanket order and create two purchase orders
            from the blanket order lines """
        blanket_order = self.blanket_order_obj.create({
            'partner_id': self.partner.id,
            'validity_date': fields.Date.to_string(self.tomorrow),
            'payment_term_id': self.payment_term.id,
            'line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_uom': self.product.uom_id.id,
                    'original_qty': 20.0,
                    'price_unit': 30.0,
                }), (0, 0, {
                    'product_id': self.product2.id,
                    'product_uom': self.product2.uom_id.id,
                    'original_qty': 50.0,
                    'price_unit': 60.0,
                })
            ],
        })
        blanket_order.onchange_partner_id()
        blanket_order.action_confirm()

        bo_lines = self.blanket_order_line_obj.search([])
        self.assertEqual(len(bo_lines), 2)

        wizard1 = self.blanket_order_wiz_obj.with_context(
            active_ids=[bo_lines[0].id, bo_lines[1].id]).create({})
        self.assertEqual(len(wizard1.line_ids), 2)
        wizard1.line_ids[0].write({'qty': 10.0})
        wizard1.line_ids[1].write({'qty': 20.0})
        wizard1.create_purchase_order()

        self.assertEqual(bo_lines[0].remaining_qty, 10.0)
        self.assertEqual(bo_lines[1].remaining_qty, 30.0)
