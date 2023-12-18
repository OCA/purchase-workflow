# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestPurchaseManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = cls.env["res.users"].create(
            {
                "name": "Test",
                "login": "test",
                "password": "password",
                "groups_id": [cls.env.ref("base.group_user").id],
            }
        )
        cls.user2 = cls.env["res.users"].create(
            {
                "name": "Test2",
                "login": "test2",
                "password": "password",
                "groups_id": [cls.env.ref("base.group_user").id],
            }
        )
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
                "purchase_manager_id": cls.user1.id,
            }
        )

    def test_purchase_manager(self):
        purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
            }
        )
        # Check user_id in purchase is equal to purchase manager in supplier
        self.assertEqual(purchase_order.user_id, self.user1)
        purchase_order.button_confirm()
        self.supplier.write({"purchase_manager_id": self.user2.id})
        # Check user_id has not changed in purchase after change purchase manager
        # in supplier and confirm purchase
        self.assertNotEqual(purchase_order.user_id, self.supplier.purchase_manager_id)
        self.assertEqual(purchase_order.user_id, self.user1)
