# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestPurchaseOrder(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.product_1 = cls.env['product.product'].create({
            'name': 'Test product 1',
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Test product 2',
        })
        po_model = cls.env['purchase.order.line']
        # Set the Exchange rate for the currency of the company to 1
        # to avoid issues with rates
        cls.env['res.currency.rate'].create({
            'currency_id': cls.env.user.company_id.currency_id.id,
            'rate': 1.00,
            'name': fields.Date.today()
            })
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.env.ref('base.res_partner_3').id,
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
            'taxes_id': [(6, 0, [cls.tax.id])],
            'price_unit': 230.0,
        })
        cls.po_line_3 = po_model.create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product_2.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 1.0,
            'product_uom': cls.product_2.uom_id.id,
            'discount': 0,
            'taxes_id': [(6, 0, [cls.tax.id])],
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
        move = moves.filtered(lambda x: x.purchase_line_id == self.po_line_1)
        self.assertEqual(move.price_unit, 5,)
        move = moves.filtered(lambda x: x.purchase_line_id == self.po_line_2)
        self.assertEqual(move.price_unit, 161)
        move = moves.filtered(lambda x: x.purchase_line_id == self.po_line_3)
        self.assertEqual(move.price_unit, 10)
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

    def test_invoice(self):
        invoice = self.env['account.invoice'].new({
            'partner_id': self.env.ref('base.res_partner_3').id,
            'purchase_id': self.purchase_order.id,
        })
        invoice.purchase_order_change()
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_1
        )
        self.assertEqual(line.discount, 50)
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_2
        )
        self.assertEqual(line.discount, 30)
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_3
        )
        self.assertEqual(line.discount, 0)
