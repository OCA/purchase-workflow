# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestPurchaseOrder(common.SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestPurchaseOrder, self).setUpClass()
        self.partner = self.env.ref('base.res_partner_1')
        self.receivable_account = self.env.ref('account.a_recv')
        self.order = self.env.ref('purchase_triple_discount.order')
        self.po_line1 = self.env.ref('purchase_triple_discount.order_line1')
        self.po_line2 = self.env.ref('purchase_triple_discount.order_line2')

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
        self.po_line1.discount = 10.0
        self.po_line1.discount2 = 20.0
        self.po_line1.discount3 = 30.0
        self.po_line2.discount3 = 40.0
        self.order.signal_workflow('purchase_confirm')
        self.invoice = self.order.invoice_ids[0]
        self.assertEqual(self.po_line1.discount,
                         self.invoice.invoice_line[0].discount)
        self.assertEqual(self.po_line1.discount2,
                         self.invoice.invoice_line[0].discount2)
        self.assertEqual(self.po_line1.discount3,
                         self.invoice.invoice_line[0].discount3)
        self.assertEqual(self.po_line2.discount3,
                         self.invoice.invoice_line[1].discount3)
        self.assertEqual(self.order.amount_total, self.invoice.amount_total)
