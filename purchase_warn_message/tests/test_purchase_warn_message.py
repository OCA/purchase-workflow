# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseWarnMessage(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warn_msg_parent = "This customer has a warn from parent"
        self.parent = self.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "purchase_warn": "warning",
                "purchase_warn_msg": self.warn_msg_parent,
            }
        )
        self.warn_msg = "This customer has a warn"
        self.partner = self.env["res.partner"].create(
            {
                "name": "Customer with a warn",
                "email": "customer@warn.com",
                "purchase_warn": "warning",
                "purchase_warn_msg": self.warn_msg,
            }
        )

    def test_compute_purchase_warn_msg(self):
        purchase = self.env["purchase.order"].create({"partner_id": self.partner.id})
        self.assertEqual(purchase.purchase_warn_msg, self.warn_msg)

    def test_compute_purchase_warn_msg_parent(self):
        self.partner.update({"parent_id": self.parent.id})
        purchase = self.env["purchase.order"].create({"partner_id": self.partner.id})
        self.assertEqual(
            purchase.purchase_warn_msg, self.warn_msg_parent + "\n" + self.warn_msg
        )
