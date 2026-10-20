# Copyright (C) 2021-Today GRAP (http://www.grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.purchase_no_rfq.hooks import uninstall_hook


@tagged("post_install", "-at_install")
class TestPurchaseNoRfq(BaseCommon):
    _test_user_groups = ("purchase.group_purchase_manager", "base.group_system")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create({"name": "Test Product"})
        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )

    def test_states_and_flow(self):
        states = dict(self.order._fields["state"]._description_selection(self.env))
        self.assertEqual(states["draft"], "Draft")
        self.assertEqual(states["sent"], "Sent")
        self.order.state = "sent"
        self.order.button_confirm()
        self.assertEqual(self.order.state, "purchase")

    def test_menu_and_action(self):
        menu = self.env.ref("purchase.menu_purchase_rfq")
        self.assertIn(self.env.ref("base.group_no_one"), menu.group_ids)
        action = self.env.ref("purchase.purchase_form_action")
        self.assertEqual(action.domain, "[]")

    def test_views(self):
        form = self.order.get_view(view_type="form")["arch"]
        self.assertNotIn("Request for Quotation", form)
        self.assertNotIn("Send RFQ", form)
        self.assertIn("Send by Email", form)
        tree_id = self.env.ref("purchase.purchase_order_view_tree").id
        tree = self.order.get_view(tree_id)["arch"]
        self.assertIn("state in ('draft','sent')", tree)

    def test_report(self):
        report = self.env["ir.actions.report"]
        html, _type = report._render_qweb_html(
            "purchase.action_report_purchase_order", self.order.ids
        )
        self.assertIn("Purchase Order #", html.decode())
        self.assertNotIn("Request for Quotation", html.decode())

    def test_uninstall_hook(self):
        uninstall_hook(self.env)
        menu = self.env.ref("purchase.menu_purchase_rfq")
        self.assertFalse(menu.group_ids)
        self.assertEqual(menu.sequence, 0)
