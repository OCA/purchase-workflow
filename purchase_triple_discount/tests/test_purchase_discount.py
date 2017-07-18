# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseOrder(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.product1 = cls.env['product.product'].create({
            'name': 'Test Product 1',
            'purchase_method': 'purchase',
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'Test Product 2',
            'purchase_method': 'purchase',
        })
        cls.tax = cls.env['account.tax'].create({
            'name': 'TAX 15%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 15.0,
        })
        cls.order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id
        })
        po_line = cls.env['purchase.order.line']
        cls.po_line1 = po_line.create({
            'order_id': cls.order.id,
            'product_id': cls.product1.id,
            'date_planned': '2018-01-19 00:00:00',
            'name': 'Line 1',
            'product_qty': 1.0,
            'product_uom': cls.product1.uom_id.id,
            'taxes_id': [(6, 0, [cls.tax.id])],
            'price_unit': 600.0,
        })
        cls.po_line2 = po_line.create({
            'order_id': cls.order.id,
            'product_id': cls.product2.id,
            'date_planned': '2018-01-19 00:00:00',
            'name': 'Line 2',
            'product_qty': 10.0,
            'product_uom': cls.product2.uom_id.id,
            'taxes_id': [(6, 0, [cls.tax.id])],
            'price_unit': 60.0,
        })

    def test_01_purchase_order_classic_discount(self):
        """ Tests with single discount """
        self.po_line1.discount = 50.0
        self.po_line2.discount = 75.0
        self.assertEqual(self.po_line1.price_subtotal, 300.0)
        self.assertEqual(self.po_line2.price_subtotal, 150.0)
        self.assertEqual(self.order.amount_untaxed, 450.0)
        self.assertEqual(self.order.amount_tax, 67.5)
        # Mix taxed and untaxed:
        self.po_line1.taxes_id = False
        self.assertEqual(self.order.amount_tax, 22.5)

    def test_02_purchase_order_simple_triple_discount(self):
        """ Tests on a single line """
        self.po_line2.unlink()
        # Divide by two on every discount:
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.assertEqual(self.po_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 75.0)
        self.assertEqual(self.order.amount_tax, 11.25)
        # Unset first discount:
        self.po_line1.discount = 0.0
        self.assertEqual(self.po_line1.price_subtotal, 150.0)
        self.assertEqual(self.order.amount_untaxed, 150.0)
        self.assertEqual(self.order.amount_tax, 22.5)
        # Set a charge instead:
        self.po_line1.discount2 = -50.0
        self.assertEqual(self.po_line1.price_subtotal, 450.0)
        self.assertEqual(self.order.amount_untaxed, 450.0)
        self.assertEqual(self.order.amount_tax, 67.5)

    def test_03_purchase_order_complex_triple_discount(self):
        """ Tests on multiple lines """
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.assertEqual(self.po_line1.price_subtotal, 75.0)
        self.assertEqual(self.order.amount_untaxed, 675.0)
        self.assertEqual(self.order.amount_tax, 101.25)
        self.po_line2.discount3 = 50.0
        self.assertEqual(self.po_line2.price_subtotal, 300.0)
        self.assertEqual(self.order.amount_untaxed, 375.0)
        self.assertEqual(self.order.amount_tax, 56.25)

    def test_04_purchase_order_triple_discount_invoicing(self):
        """ When a confirmed order is invoiced, the resultant invoice
            should inherit the discounts """
        self.po_line1.discount = 50.0
        self.po_line1.discount2 = 50.0
        self.po_line1.discount3 = 50.0
        self.po_line2.discount3 = 50.0
        self.order.button_confirm()
        self.invoice = self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'purchase_id': self.order.id,
            'account_id': self.partner.property_account_payable_id.id,
            'type': 'in_invoice',
        })
        self.invoice.purchase_order_change()
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.po_line1.discount,
                         self.invoice.invoice_line_ids[0].discount)
        self.assertEqual(self.po_line1.discount2,
                         self.invoice.invoice_line_ids[0].discount2)
        self.assertEqual(self.po_line1.discount3,
                         self.invoice.invoice_line_ids[0].discount3)
        self.assertEqual(self.po_line2.discount3,
                         self.invoice.invoice_line_ids[1].discount3)
        self.assertEqual(self.order.amount_total, self.invoice.amount_total)
