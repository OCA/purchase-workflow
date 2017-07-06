# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


class TestPurchaseSupplierRoundingMethod(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseSupplierRoundingMethod, self).setUp()

    def test_1_account_invoice_rounding_method(self):
        """Test 'Normal' and 'Round Net Price' supplier rounding method
        on a Suupplier Invoice"""
        # Set a Net price to 0.6667
        line = self.browse_ref(
            'purchase_supplier_rounding_method.invoice_1_line_a')

        line.quantity = 1000
        line.price_unit = 1
        line.discount = 33.33
        self.assertEquals(line.price_subtotal, 670)

        # Change to a normal partner
        line.invoice_id.partner_id = self.browse_ref('base.res_partner_12')
        self.assertEquals(line.price_subtotal, 666.70)

    def test_2_purchase_order_rounding_method(self):
        """Test 'Normal' and 'Round Net Price' supplier rounding method
        on a Purchase Order"""
        # Set a Net price to 0.6667
        line = self.browse_ref(
            'purchase_supplier_rounding_method.purchase_order_1_line_a')

        line.product_qty = 1000
        line.price_unit = 1
        line.discount = 33.33
        self.assertEquals(line.price_subtotal, 670)
        self.assertEquals(
            round(line._calc_line_base_price(line), 4), 0.67)

        # Change to a normal partner and recompute subtotal
        line.order_id.partner_id = self.browse_ref('base.res_partner_12')
        line.product_qty = 10000
        self.assertEquals(line.price_subtotal, 6667.00)
        self.assertEquals(
            round(line._calc_line_base_price(line), 4), 0.6667)
