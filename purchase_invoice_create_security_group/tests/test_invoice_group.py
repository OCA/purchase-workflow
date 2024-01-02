# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class TestPurchaseInvoiceGroup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.purchase_obj = cls.env["purchase.order"]
        cls.product = cls.env.ref("product.product_product_2")
        cls.group = cls.env.ref(
            "purchase_invoice_create_security_group.group_purchase_invoice_create"
        )
        cls.product.purchase_method = "purchase"
        cls.env.company.purchase_invoice_create_security = True

    @classmethod
    def create_purchase(cls):
        vals = {
            "name": "Purchase 1",
            "partner_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product.id,
                    },
                )
            ],
        }
        cls.purchase = cls.purchase_obj.create(vals)

    def test_invoice_not_group(self):
        self.create_purchase()
        self.purchase.button_confirm()
        with self.assertRaises(AccessError):
            self.purchase.action_create_invoice()

    def test_invoice_group(self):
        self.env.user.groups_id |= self.group
        self.create_purchase()
        self.purchase.button_confirm()
        self.purchase.action_create_invoice()

    def test_invoice_not_activated(self):
        self.env.company.purchase_invoice_create_security = False
        self.env.company.invalidate_cache()
        self.create_purchase()
        self.purchase.button_confirm()
        self.purchase.action_create_invoice()
