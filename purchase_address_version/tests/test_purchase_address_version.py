# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseAddressVersion(TransactionCase):
    def setUp(self):
        super(TestPurchaseAddressVersion, self).setUp()
        self.purchase = self.env.ref("purchase.purchase_order_2")

    def test_purchase_address_version(self):
        self.assertFalse(self.purchase.partner_address_id.version_hash)
        self.purchase.button_confirm()
        self.assertTrue(self.purchase.partner_address_id.version_hash)
