# Copyright 2026 Moduon
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import HttpCase, tagged
from odoo.tests.common import new_test_user


@tagged("post_install", "-at_install")
class TestPurchaseOrderLineDescriptionUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tour_user = new_test_user(
            cls.env,
            login="pol_description_tour_user",
            groups="purchase.group_purchase_user",
            context={"no_reset_password": True, "mail_create_nosubscribe": True},
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        # Resolve compatibility with purchase.order.type in tours
        if "purchase.order.type" in cls.env:
            cls.partner.purchase_type = cls.env["purchase.order.type"].search(
                [], limit=1
            )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "description_purchase": "Purchase description for test product",
            }
        )
        cls.purchase_order = (
            cls.env["purchase.order"]
            .with_user(cls.tour_user)
            .create(
                {
                    "partner_id": cls.partner.id,
                    "order_line": [Command.create({"product_id": cls.product.id})],
                }
            )
        )

    def test_manual_description_edit_keeps_product_name_hidden_tour(self):
        self.assertEqual(
            self.purchase_order.order_line.name,
            self.product.description_purchase,
        )

        self.start_tour(
            f"/odoo/purchase-orders/{self.purchase_order.id}",
            "purchase_order_line_description_manual_edit",
            login="pol_description_tour_user",
        )

        self.purchase_order.order_line.invalidate_recordset(["name"])
        self.assertEqual(
            self.purchase_order.order_line.name,
            f"{self.product.description_purchase} test",
        )
