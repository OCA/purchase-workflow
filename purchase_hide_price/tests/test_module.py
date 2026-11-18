from lxml import etree

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import Form
from odoo.tests.common import TransactionCase, new_test_user


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": "my partner", "country_id": cls.env.ref("base.us").id}
        )
        cls.contact = cls.child_partner = cls.env["res.partner"].create(
            {"parent_id": cls.partner.id, "name": "my child"}
        )
        cls.product = cls.env["product.product"].create({"name": "my product"})
        cls.user = new_test_user(
            cls.env,
            login="hide_price_user",
            groups="purchase.group_purchase_user,"
            "purchase_hide_price.purchase_hide_price_grp",
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.contact.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "price_unit": 7})
                ],
            }
        )

    def test_standard_behavior(self):
        po = self.purchase
        self.assertNotEqual(po.amount_total, 0)
        self.assertEqual(po.amount_total_hide, po.amount_total)
        self.assertEqual(po.amount_untaxed_hide, po.amount_untaxed)
        line = po.order_line[0]
        self.assertEqual(line.price_unit_hide, line.price_unit)
        self.assertEqual(line.price_subtotal_hide, line.price_subtotal)
        self.assertEqual(line.price_total_hide, line.price_total)

    def test_hidden_prices(self):
        po = self.purchase
        self.contact.commercial_partner_id.hide_purchase_price = True
        self.env.user.groups_id = [
            Command.link(self.env.ref("purchase_hide_price.purchase_hide_price_grp").id)
        ]
        # standard behavior
        self.assertNotEqual(po.amount_total, 0)
        # module behavior
        self.assertEqual(po.amount_total_hide, 0)
        self.assertEqual(po.amount_untaxed_hide, 0)
        line = po.order_line[0]
        self.assertEqual(line.price_unit_hide, 0)
        self.assertEqual(line.price_subtotal_hide, 0)
        self.assertEqual(line.price_total_hide, 0)

    def test_partial_config(self):
        """In that case, standard behavior happens"""
        po = self.purchase
        partner = self.partner.commercial_partner_id
        partner.hide_purchase_price = False
        # standard behavior
        self.assertNotEqual(po.amount_total_hide, 0)
        partner.hide_purchase_price = True
        # missing group
        self.assertNotEqual(po.amount_total_hide, 0)
        partner.hide_purchase_price = False
        self.env.user.groups_id = [
            Command.link(self.env.ref("purchase_hide_price.purchase_hide_price_grp").id)
        ]
        # missing impacted vendor
        self.assertNotEqual(po.amount_total_hide, 0)

    def test_vendor_contact_hide_has_no_effect(self):
        po = self.purchase
        self.partner.hide_purchase_price = False
        # No effect, it must be configured on the commercial partner_id instead
        self.contact.hide_purchase_price = True
        self.env.user.groups_id = [
            Command.link(self.env.ref("purchase_hide_price.purchase_hide_price_grp").id)
        ]
        # module behavior
        self.assertNotEqual(po.amount_total_hide, 0)

    def test_hidden_vendor_price_is_used(self):
        """Vendor price must be applied even if hidden to the user"""
        self.partner.hide_purchase_price = True
        self.product.standard_price = 10
        seller = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 100,
            }
        )
        user = self.user
        self.assertTrue(seller.with_user(user).hide_price)
        self.assertFalse(seller.hide_price)
        po = (
            self.env["purchase.order"]
            .with_user(user)
            .create(
                {
                    "partner_id": self.contact.id,
                    "order_line": [Command.create({"product_id": self.product.id})],
                }
            )
        )
        self.assertEqual(po.order_line.price_unit, 100)
        self.assertEqual(po.order_line.price_unit_hide, 0)

    def test_hide_field_restricted_to_manager(self):
        with self.assertRaises(AccessError):
            self.partner.with_user(self.user).hide_purchase_price = False

    def test_report_hides_prices(self):
        self.partner.hide_purchase_price = True
        self.purchase.order_line.price_unit = 123456
        report = self.env["ir.actions.report"].with_user(self.user)
        html = report._render_qweb_html(
            "purchase.action_report_purchase_order", self.purchase.ids
        )[0].decode()
        self.assertNotIn("123,456", html)
        self.assertIn("my product", html)

    def test_form_view_has_no_price_field(self):
        """List, form and kanban order line subviews must not expose prices"""
        arch = (
            self.env["purchase.order"]
            .with_user(self.user)
            .get_view(view_type="form")["arch"]
        )
        # arch may be str or bytes depending on installed modules
        doc = etree.fromstring(arch)
        for fname in ("price_unit", "price_subtotal", "price_total"):
            self.assertFalse(doc.xpath(f"//field[@name='{fname}']"), fname)

    def test_hidden_fields_computed_before_save(self):
        """Not hidden vendor: displayed price is right while editing"""
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 100,
            }
        )
        po_form = Form(self.env["purchase.order"].with_user(self.user))
        po_form.partner_id = self.partner
        with po_form.order_line.new() as line:
            line.product_id = self.product
            self.assertEqual(line.price_unit_hide, 100)
            self.assertEqual(line.price_subtotal_hide, 100)
