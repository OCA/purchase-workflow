# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestPurchaseOrder(common.HttpCase):
    at_install = False
    post_install = False

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        self.company = self.env.user.company_id
        self.company.tax_calculation_rounding_method = 'round_per_line'
        self.product_1 = self.env['product.product'].create({
            'name': 'Test product 1',
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Test product 2',
        })
        po_model = self.env['purchase.order.line']
        # Make sure currency is EUR for not having troubles with rates
        self.env.user.company_id.currency_id = self.env.ref('base.EUR')
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.env.ref('base.res_partner_3').id,
        })
        self.po_line_1 = po_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_1.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': self.product_1.uom_id.id,
            'discount': 50.0,
            'price_unit': 10.0,
        })
        self.tax = self.env['account.tax'].create({
            'name': 'Sample tax 15%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 15.0,
        })
        self.po_line_2 = po_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_2.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 10.0,
            'product_uom': self.product_2.uom_id.id,
            'discount': 30,
            'taxes_id': [(6, 0, [self.tax.id])],
            'price_unit': 230.0,
        })
        self.po_line_3 = po_model.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product_2.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': self.product_2.uom_id.id,
            'discount': 0,
            'taxes_id': [(6, 0, [self.tax.id])],
            'price_unit': 10.0,
        })

    def test_purchase_order_vals(self):
        self.assertEqual(self.po_line_1.price_subtotal, 5.0)
        self.assertEqual(self.po_line_2.price_subtotal, 1610.0)
        self.assertEqual(self.po_line_3.price_subtotal, 10.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1625.0)
        self.assertEqual(self.purchase_order.amount_tax, 243)

    def test_move_price_unit(self):
        self.purchase_order.button_confirm()
        moves = self.purchase_order.picking_ids.move_lines
        self.assertEqual(moves[0].price_unit, 5,)
        self.assertEqual(moves[1].price_unit, 161)
        self.assertEqual(moves[2].price_unit, 10)
        # Change price to launch a recalculation of totals
        self.po_line_1.discount = 60
        self.assertEqual(self.po_line_1.price_subtotal, 4.0)
        self.assertEqual(self.purchase_order.amount_untaxed, 1624.0)
        self.assertEqual(self.purchase_order.amount_tax, 243)

    def test_report_price_unit(self):
        rec = self.env['purchase.report'].search([
            ('product_id', '=', self.product_1.id),
        ])
        self.assertEqual(rec.price_total, 5)
        self.assertEqual(rec.discount, 50)


class TestPurchaseOrderRoundGlobally(TestPurchaseOrder):
    def setUp(self):
        super(TestPurchaseOrderRoundGlobally, self).setUp()
        self.company.tax_calculation_rounding_method = 'round_globally'
