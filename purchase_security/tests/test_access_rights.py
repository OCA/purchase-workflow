# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestPurchaseOrderSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderSecurity, cls).setUpClass()
        # Users
        users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.team1 = cls.env["purchase.team"].create({"name": "Team1"})
        cls.team2 = cls.env["purchase.team"].create({"name": "Team2"})
        # User in group_purchase_own_orders
        cls.user_group_purchase_own_orders = users.create(
            {
                "name": "group_purchase_own_orders",
                "login": "group_purchase_own_orders",
                "email": "group_purchase_own_orders@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [cls.env.ref("purchase_security.group_purchase_own_orders").id],
                    )
                ],
            }
        )
        # User 1 in group_purchase_group_orders
        cls.user_group_team_1 = users.create(
            {
                "name": "group_purchase_team_1_orders",
                "login": "group_purchase_team_1_orders",
                "email": "group_purchase_team_1_orders@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "purchase_security.group_purchase_group_orders"
                            ).id
                        ],
                    )
                ],
            }
        )
        # Adding user 1 to both teams
        cls.team1.write({"user_ids": [(4, cls.user_group_team_1.id)]})
        cls.team2.write({"user_ids": [(4, cls.user_group_team_1.id)]})
        # User 2 in group_purchase_group_orders
        cls.user_group_team_2 = users.create(
            {
                "name": "group_purchase_team_2_orders",
                "login": "group_purchase_team_2_orders",
                "email": "group_purchase_team_2_orders@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "purchase_security.group_purchase_group_orders"
                            ).id
                        ],
                    )
                ],
            }
        )
        # Adding user 2 to only one team
        cls.team1.write({"user_ids": [(4, cls.user_group_team_2.id)]})
        # User with group permission but without being assigned to any team
        cls.user_group_team_3 = users.create(
            {
                "name": "group_purchase_team_3_orders",
                "login": "group_purchase_team_3_orders",
                "email": "group_purchase_team_3_orders@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "purchase_security.group_purchase_group_orders"
                            ).id
                        ],
                    )
                ],
            }
        )
        # Purchase order user
        cls.user_po_user = users.create(
            {
                "name": "po_user",
                "login": "po_user",
                "email": "po_user@example.com",
                "groups_id": [(6, 0, [cls.env.ref("purchase.group_purchase_user").id])],
            }
        )
        # Purchase order manager
        cls.user_po_manager = users.create(
            {
                "name": "po_manager",
                "login": "po_manager",
                "email": "po_manager@example.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("purchase.group_purchase_manager").id])
                ],
            }
        )
        # User without groups
        cls.user_without_groups = users.create(
            {
                "name": "without_groups",
                "login": "without_groups",
                "email": "without_groups@example.com",
                "groups_id": False,
            }
        )
        # Partner for the POs
        cls.partner_po = cls.env["res.partner"].create({"name": "PO Partner"})
        # Purchase Order
        cls.orders = cls.env["purchase.order"].create(
            (
                {
                    "name": "po_security_1",
                    "partner_id": cls.partner_po.id,
                    "user_id": False,  # No Purchase Representative
                },
                {
                    "name": "po_security_2",
                    "user_id": cls.user_po_user.id,
                    "partner_id": cls.partner_po.id,
                },
                {
                    "name": "po_security_3",
                    "user_id": cls.user_po_manager.id,
                    "partner_id": cls.partner_po.id,
                    "team_id": cls.team1.id,
                },
                {
                    "name": "po_security_4",
                    "user_id": cls.user_group_purchase_own_orders.id,
                    "partner_id": cls.partner_po.id,
                    "team_id": cls.team2.id,
                },
            )
        )

    def test_access_user_user_group_purchase_own_orders(self):
        # User in group should have access to it's own PO
        # and to those w/o Purchase Representative
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_purchase_own_orders)
                .search([])
                .ids
            ),
            2,
        )
        self.assertFalse(
            self.orders.filtered(
                lambda x: x.user_id == self.user_group_purchase_own_orders
            )
            .with_user(self.user_group_purchase_own_orders)[0]
            .is_user_id_editable
        )

    def test_access_user_po_user(self):
        # Normal PO user should have access to all of them
        # because he is not in group
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_po_user)
                .search([("name", "like", "po_security")])
                .ids
            ),
            4,
        )
        self.assertTrue(self.orders.with_user(self.user_po_user)[0].is_user_id_editable)

    def test_access_user_po_manager(self):
        # Manager PO user should have access to all of them
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_po_manager)
                .search([("name", "like", "po_security")])
                .ids
            ),
            4,
        )
        self.assertTrue(
            self.orders.with_user(self.user_po_manager)[1].is_user_id_editable
        )

    def test_access_user_without_groups(self):
        # User without groups should not have access to POs
        self.assertEqual(
            len(self.env["purchase.order"].with_user(self.user_without_groups).read()),
            0,
        )

    def test_access_user_user_group_purchase_group_orders_1(self):
        # User in group should have access PO's without any team assigned,
        # and to those to whose team he belongs. In this case, it belongs to
        # both teams
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_team_1)
                .search([("name", "like", "po_security")])
                .ids
            ),
            4,
        )

    def test_access_user_user_group_purchase_group_orders_2(self):
        # User in group should have access PO's without any team assigned,
        # and to those to whose team he belongs. In this case, it belongs to
        # only one team, so the other order won't be seen
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_team_2)
                .search([("name", "like", "po_security")])
                .ids
            ),
            3,
        )

    def test_access_user_user_group_purchase_group_orders_3(self):
        # User in group should have access PO's without any team assigned,
        # and to those to whose team he belongs. In this case, it does not
        # belongs to any team, so the other orders won't be seen
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_team_3)
                .search([("name", "like", "po_security")])
                .ids
            ),
            2,
        )
