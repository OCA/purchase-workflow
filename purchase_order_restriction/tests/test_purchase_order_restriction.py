# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseOrderRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderRestriction, cls).setUpClass()
        purchase_user_group = cls.env.ref("purchase.group_purchase_user")
        purchase_manager_group = cls.env.ref("purchase.group_purchase_manager")
        # User in group_purchase_user
        cls.user1 = cls._create_user(cls, "User 1", "user 1", purchase_user_group)
        cls.user2 = cls._create_user(cls, "User 2", "user 2", purchase_user_group)
        # Purchase order manager
        cls.user_manager = cls._create_user(
            cls,
            "Manager",
            "manager",
            purchase_manager_group,
        )
        # Partner for the POs
        cls.partner = cls.env["res.partner"].create({"name": "PO Partner"})
        # Purchase Order
        cls.po_1 = cls._create_order(cls, "Purchaser Order 1", cls.user1.id)
        cls.po_2 = cls._create_order(cls, "Purchaser Order 2", cls.user2.id)
        cls.po_3 = cls._create_order(cls, "Purchaser Order 3")

    def _create_user(self, name, login, group):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "login": login,
                    "email": "test@yourcompany.com",
                    "groups_id": [(6, 0, [group.id])],
                }
            )
        )

    def _create_order(self, name, user_id=False):
        return self.env["purchase.order"].create(
            {"name": name, "partner_id": self.partner.id, "user_id": user_id},
        )

    def search_order(self, user):
        return (
            self.env["purchase.order"]
            .with_user(user)
            .search([("name", "like", "Purchaser Order")])
        )

    def test_order_restriction(self):
        # PO user should have access to all of them
        # before it's restricted
        self.assertEqual(len(self.search_order(self.user1)), 3)
        self.assertEqual(len(self.search_order(self.user2)), 3)
        self.assertEqual(len(self.search_order(self.user_manager)), 3)
        # when user2 restrict user1's PO, error will be raised
        with self.assertRaises(ValidationError):
            self.po_1.with_user(self.user2).write({"is_restricted": True})
        # After user1 restricted his own PO
        self.po_1.with_user(self.user1).write({"is_restricted": True})
        self.assertEqual(len(self.search_order(self.user1)), 3)
        self.assertEqual(len(self.search_order(self.user2)), 2)
        self.assertEqual(len(self.search_order(self.user_manager)), 3)
