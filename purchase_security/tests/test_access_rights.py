# Copyright 2020 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Stefan Ungureanu
# Copyright 2023 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users


class TestPurchaseOrderSecurity(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        # Teams
        cls.team1 = cls.env["purchase.team"].create({"name": "Team1"})
        cls.team2 = cls.env["purchase.team"].create({"name": "Team2"})
        # Users
        # User in group_purchase_own_orders
        cls.user_group_purchase_own_orders = new_test_user(
            cls.env,
            login="group_purchase_own_orders",
            groups="purchase_security.group_purchase_own_orders",
        )
        # User 1 in group_purchase_group_orders
        cls.user_group_team_1 = new_test_user(
            cls.env,
            login="group_purchase_team_1_orders",
            groups="purchase_security.group_purchase_group_orders",
        )
        # Adding user 1 to both teams
        cls.team1.write({"user_ids": [(4, cls.user_group_team_1.id)]})
        cls.team2.write({"user_ids": [(4, cls.user_group_team_1.id)]})
        # User 2 in group_purchase_group_orders
        cls.user_group_team_2 = new_test_user(
            cls.env,
            login="group_purchase_team_2_orders",
            groups="purchase_security.group_purchase_group_orders",
        )
        # Adding user 2 to only one team
        cls.team1.write({"user_ids": [(4, cls.user_group_team_2.id)]})
        # User with group permission but without being assigned to any team
        cls.user_group_team_3 = new_test_user(
            cls.env,
            login="group_purchase_team_3_orders",
            groups="purchase_security.group_purchase_group_orders",
        )
        # Purchase order user
        cls.user_po_user = new_test_user(
            cls.env, login="po_user", groups="purchase.group_purchase_user"
        )
        # Purchase order manager
        cls.user_po_manager = new_test_user(
            cls.env, login="po_manager", groups="purchase.group_purchase_manager"
        )
        # User without groups
        cls.user_without_groups = new_test_user(cls.env, login="without_groups")
        # Partner for the POs
        cls.partner_po = cls.env["res.partner"].create({"name": "PO Partner"})
        # Purchase Order
        cls.orders = cls.env["purchase.order"].create(
            (
                {
                    "name": "po_security_1",
                    "partner_id": cls.partner_po.id,
                    "user_id": False,  # No Purchase Representative
                    "team_id": False,  # No automatic team
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

    @users("group_purchase_team_1_orders")
    def test_new_purchase_order(self):
        order_form_1 = Form(self.env["purchase.order"])
        self.assertEqual(order_form_1.user_id, self.user_group_team_1)
        self.assertEqual(order_form_1.team_id, self.team1)
        order_form_1.partner_id = self.partner_po
        self.assertEqual(order_form_1.user_id, self.user_group_team_1)
        self.assertEqual(order_form_1.team_id, self.team1)
        # order_form with default_user_id (user_group_team_2 > team_2)
        self.team1.write({"user_ids": [(3, self.user_group_team_2.id)]})
        self.team2.write({"user_ids": [(4, self.user_group_team_2.id)]})
        order_form_2 = Form(
            self.env["purchase.order"].with_context(
                default_user_id=self.user_group_team_2.id
            )
        )
        self.assertEqual(order_form_2.user_id, self.user_group_team_2)
        self.assertEqual(order_form_2.team_id, self.team2)
        order_form_2.partner_id = self.partner_po
        self.assertEqual(order_form_2.user_id, self.user_group_team_2)
        self.assertEqual(order_form_2.team_id, self.team2)
        # order_form with default_user_id (user_group_team_3 > without team)
        order_form_2 = Form(
            self.env["purchase.order"].with_context(
                default_user_id=self.user_group_team_3.id
            )
        )
        self.assertEqual(order_form_2.user_id, self.user_group_team_3)
        self.assertEqual(order_form_2.team_id, self.team1)
        order_form_2.partner_id = self.partner_po
        self.assertEqual(order_form_2.user_id, self.user_group_team_3)
        self.assertEqual(order_form_2.team_id, self.team1)

    def _check_permission(self, user, team, expected):
        self.partner_po.write(
            {
                "purchase_user_id": user.id if user else user,
                "purchase_team_id": team.id if team else team,
            }
        )
        domain = [("id", "=", self.partner_po.id)]
        obj = self.env[self.partner_po._name]
        self.assertEqual(bool(obj.search(domain)), expected)

    def test_po_auto_team(self):
        order = self.env["purchase.order"].search([("name", "=", "po_security_2")])
        self.assertEqual(order.team_id, self.team1)

    def test_access_user_user_group_purchase_own_orders(self):
        # User in group should have access to it's own PO
        # and to those w/o Purchase Representative
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_purchase_own_orders)
                .search([])
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
            ),
            3,
        )

    def test_access_user_user_group_purchase_group_orders_3(self):
        # User in group should have access PO's without any team assigned,
        # and to those to whose team they belongs. In this case, it does not
        # belongs to any team, so the other orders won't be seen
        self.assertEqual(
            len(
                self.env["purchase.order"]
                .with_user(self.user_group_team_3)
                .search([("name", "like", "po_security")])
            ),
            1,
        )

    @users("po_user")
    def test_partner_permissions_01(self):
        """User with purchase.group_purchase_user group."""
        self._check_permission(False, False, True)
        self._check_permission(False, self.team1, True)
        self._check_permission(False, self.team2, True)
        self._check_permission(self.user_group_purchase_own_orders, False, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team1, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team2, True)
        self._check_permission(self.user_group_team_1, False, True)
        self._check_permission(self.user_group_team_1, self.team1, True)
        self._check_permission(self.user_group_team_1, self.team2, True)
        self._check_permission(self.user_group_team_2, False, True)
        self._check_permission(self.user_group_team_2, self.team1, True)
        self._check_permission(self.user_group_team_2, self.team2, True)
        self._check_permission(self.user_group_team_3, False, True)
        self._check_permission(self.user_group_team_3, self.team1, True)
        self._check_permission(self.user_group_team_3, self.team2, True)
        self._check_permission(self.user_po_user, False, True)
        self._check_permission(self.user_po_user, self.team1, True)
        self._check_permission(self.user_po_user, self.team2, True)
        self._check_permission(self.user_po_manager, False, True)
        self._check_permission(self.user_po_manager, self.team1, True)
        self._check_permission(self.user_po_manager, self.team2, True)
        self._check_permission(self.user_without_groups, False, True)
        self._check_permission(self.user_without_groups, self.team1, True)
        self._check_permission(self.user_without_groups, self.team2, True)

    @users("group_purchase_own_orders")
    def test_partner_permissions_02(self):
        """User with purchase_security.group_purchase_own_orders group."""
        self._check_permission(False, False, True)
        self._check_permission(False, self.team1, False)
        self._check_permission(False, self.team2, False)
        self._check_permission(self.user_group_purchase_own_orders, False, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team1, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team2, True)
        self._check_permission(self.user_group_team_1, False, False)
        self._check_permission(self.user_group_team_1, self.team1, False)
        self._check_permission(self.user_group_team_1, self.team2, False)
        self._check_permission(self.user_group_team_2, False, False)
        self._check_permission(self.user_group_team_2, self.team1, False)
        self._check_permission(self.user_group_team_2, self.team2, False)
        self._check_permission(self.user_group_team_3, False, False)
        self._check_permission(self.user_group_team_3, self.team1, False)
        self._check_permission(self.user_group_team_3, self.team2, False)
        self._check_permission(self.user_po_user, False, False)
        self._check_permission(self.user_po_user, self.team1, False)
        self._check_permission(self.user_po_user, self.team2, False)
        self._check_permission(self.user_po_manager, False, False)
        self._check_permission(self.user_po_manager, self.team1, False)
        self._check_permission(self.user_po_manager, self.team2, False)
        self._check_permission(self.user_without_groups, False, False)
        self._check_permission(self.user_without_groups, self.team1, False)
        self._check_permission(self.user_without_groups, self.team2, False)

    @users("group_purchase_team_1_orders")
    def test_partner_permissions_03(self):
        """User with purchase_security.group_purchase_group_orders group."""
        self._check_permission(False, False, True)
        self._check_permission(False, self.team1, True)
        self._check_permission(False, self.team2, False)
        self._check_permission(self.user_group_purchase_own_orders, False, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team1, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team2, False)
        self._check_permission(self.user_group_team_1, False, True)
        self._check_permission(self.user_group_team_1, self.team1, True)
        self._check_permission(self.user_group_team_1, self.team2, False)
        self._check_permission(self.user_group_team_2, False, True)
        self._check_permission(self.user_group_team_2, self.team1, True)
        self._check_permission(self.user_group_team_2, self.team2, False)
        self._check_permission(self.user_group_team_3, False, True)
        self._check_permission(self.user_group_team_3, self.team1, True)
        self._check_permission(self.user_group_team_3, self.team2, False)
        self._check_permission(self.user_po_user, False, True)
        self._check_permission(self.user_po_user, self.team1, True)
        self._check_permission(self.user_po_user, self.team2, False)
        self._check_permission(self.user_po_manager, False, True)
        self._check_permission(self.user_po_manager, self.team1, True)
        self._check_permission(self.user_po_manager, self.team2, False)
        self._check_permission(self.user_without_groups, False, True)
        self._check_permission(self.user_without_groups, self.team1, True)
        self._check_permission(self.user_without_groups, self.team2, False)

    @users("po_manager")
    def test_partner_permissions_04(self):
        """User with purchase.group_purchase_manager group."""
        self._check_permission(False, False, True)
        self._check_permission(False, self.team1, True)
        self._check_permission(False, self.team2, True)
        self._check_permission(self.user_group_purchase_own_orders, False, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team1, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team2, True)
        self._check_permission(self.user_group_team_1, False, True)
        self._check_permission(self.user_group_team_1, self.team1, True)
        self._check_permission(self.user_group_team_1, self.team2, True)
        self._check_permission(self.user_group_team_2, False, True)
        self._check_permission(self.user_group_team_2, self.team1, True)
        self._check_permission(self.user_group_team_2, self.team2, True)
        self._check_permission(self.user_group_team_3, False, True)
        self._check_permission(self.user_group_team_3, self.team1, True)
        self._check_permission(self.user_group_team_3, self.team2, True)
        self._check_permission(self.user_po_user, False, True)
        self._check_permission(self.user_po_user, self.team1, True)
        self._check_permission(self.user_po_user, self.team2, True)
        self._check_permission(self.user_po_manager, False, True)
        self._check_permission(self.user_po_manager, self.team1, True)
        self._check_permission(self.user_po_manager, self.team2, True)
        self._check_permission(self.user_without_groups, False, True)
        self._check_permission(self.user_without_groups, self.team1, True)
        self._check_permission(self.user_without_groups, self.team2, True)

    @users("without_groups")
    def test_partner_permissions_05(self):
        """User witout groups"""
        self._check_permission(False, False, True)
        self._check_permission(False, self.team1, True)
        self._check_permission(False, self.team2, True)
        self._check_permission(self.user_group_purchase_own_orders, False, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team1, True)
        self._check_permission(self.user_group_purchase_own_orders, self.team2, True)
        self._check_permission(self.user_group_team_1, False, True)
        self._check_permission(self.user_group_team_1, self.team1, True)
        self._check_permission(self.user_group_team_1, self.team2, True)
        self._check_permission(self.user_group_team_2, False, True)
        self._check_permission(self.user_group_team_2, self.team1, True)
        self._check_permission(self.user_group_team_2, self.team2, True)
        self._check_permission(self.user_group_team_3, False, True)
        self._check_permission(self.user_group_team_3, self.team1, True)
        self._check_permission(self.user_group_team_3, self.team2, True)
        self._check_permission(self.user_po_user, False, True)
        self._check_permission(self.user_po_user, self.team1, True)
        self._check_permission(self.user_po_user, self.team2, True)
        self._check_permission(self.user_po_manager, False, True)
        self._check_permission(self.user_po_manager, self.team1, True)
        self._check_permission(self.user_po_manager, self.team2, True)
        self._check_permission(self.user_without_groups, False, True)
        self._check_permission(self.user_without_groups, self.team1, True)
        self._check_permission(self.user_without_groups, self.team2, True)
