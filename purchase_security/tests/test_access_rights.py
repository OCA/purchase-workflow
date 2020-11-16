# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestPurchaseOrderSecurity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderSecurity, cls).setUpClass()
        # Users
        users = cls.env["res.users"].with_context(no_reset_password=True)
        group_name = "group_purchase_own_orders"
        # User in group_purchase_own_orders
        cls.user_group_purchase_own_orders = users.create(
            {
                "name": "group_purchase_own_orders",
                "login": "group_purchase_own_orders",
                "email": "group_purchase_own_orders@example.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("purchase_security.%s" % group_name).id])
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
        cls.env["purchase.order"].create(
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
                },
                {
                    "name": "po_security_4",
                    "user_id": cls.user_group_purchase_own_orders.id,
                    "partner_id": cls.partner_po.id,
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

    def test_access_user_without_groups(self):
        # User without groups should not have access to POs
        self.assertEqual(
            len(self.env["purchase.order"].with_user(self.user_without_groups).read()),
            0,
        )
