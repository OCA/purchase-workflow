# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.purchase_supplier_rounding_method.tests.\
    test_purchase_supplier_rounding_method import\
    TestPurchaseSupplierRoundingMethod as TestRoundingMethod


class TestModule(TestRoundingMethod):

    def setUp(self):
        super(TestModule, self).setUp()

    def test_1_account_invoice_rounding_method(self):
        """Test 'Normal' and 'Round Net Price' supplier rounding method
        on a Supplier Invoice"""
        self._test_1_account_invoice_rounding_method()

    def test_2_purchase_order_rounding_method(self):
        super(TestModule, self).test_2_purchase_order_rounding_method()
