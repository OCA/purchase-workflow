from odoo import Command
from odoo.tests.common import TransactionCase


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
