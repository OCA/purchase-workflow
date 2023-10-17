# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchaseTransportMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env["base"].with_context(**DISABLED_MAIL_CONTEXT).env
        cls.product_a = cls.env.ref("product.consu_delivery_01")
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
            }
        )
        cls.env["purchase.order.line"].create(
            {
                "order_id": cls.purchase_order.id,
                "name": cls.product_a.name,
                "product_id": cls.product_a.id,
                "product_qty": 5,
            }
        )

        cls.transport_mode_a = cls.env["purchase.transport.mode"].create(
            {"name": "Transport mode A"}
        )
        cls.constraint_a = cls.env["purchase.transport.mode.constraint"].create(
            {
                "name": "Constraint A",
                "description": "The total amount of the order must be higher than 5000",
                "purchase_transport_mode_id": cls.transport_mode_a.id,
                "purchase_domain": [("amount_total", ">", 5000)],
            }
        )

    def enable_purchase_transport_mode_validation(self):
        self.settings = self.env["res.config.settings"].create({})
        self.settings.purchase_transport_mode_contraint_enabled = True
        self.settings.set_values()

    def test_disabled_purchase_transport_mode_validation(self):
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.state, "purchase")

    def test_purchase_transport_mode_validation(self):
        self.enable_purchase_transport_mode_validation()
        self.purchase_order.transport_mode_id = self.transport_mode_a
        self.purchase_order.button_confirm()
        self.assertFalse(self.purchase_order.transport_mode_status_ok)
        self.assertEqual(self.purchase_order.state, "draft")
        self.assertEqual(
            self.purchase_order.transport_mode_status,
            {
                "errors": [
                    "Constraint A: The total amount of the order must be higher than 5000"
                ]
            },
        )
        self.purchase_order.order_line.product_qty = 500
        self.purchase_order.invalidate_cache()
        self.purchase_order.button_confirm()
        self.assertEqual(self.purchase_order.state, "purchase")

    def test_filter_valid_purchase(self):
        self.assertEqual(
            self.constraint_a.filter_valid_purchase(self.purchase_order),
            self.env["purchase.order"],
        )
        self.constraint_a.purchase_domain = []
        self.assertEqual(
            self.constraint_a.filter_valid_purchase(self.purchase_order),
            self.purchase_order,
        )
