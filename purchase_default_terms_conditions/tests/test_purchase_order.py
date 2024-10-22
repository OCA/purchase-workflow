# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPurchase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPurchase, cls).setUpClass()
        uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.env.ref("uom.product_uom_hour")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Zed+ Antivirus",
                "standard_price": 235.0,
                "list_price": 280.0,
                "type": "consu",
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "purchase_method": "purchase",
                "default_code": "PROD_ORDER",
                "taxes_id": False,
            }
        )
        cls.partner_a.write(
            {"purchase_note": "Purchase Default Terms and Conditions Partner"}
        )

        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "partner_1",
                "company_id": cls.env.company.id,
                "purchase_note": "Sale Default Terms and Conditions Partner",
            }
        )
        cls.partner_3 = cls.env["res.partner"].create(
            {
                "name": "partner_3",
                "company_id": cls.env.company.id,
                "parent_id": cls.partner_1.id,
            }
        )
        cls.partner_4 = cls.env["res.partner"].create(
            {
                "name": "partner_3",
                "company_id": cls.env.company.id,
                "parent_id": cls.partner_1.id,
                "purchase_note": "Partner4",
            }
        )

    def test_onchange_partner_id(self):

        purchase_order = (
            self.env["purchase.order"]
            .with_context(tracking_disable=True)
            .sudo()
            .create(
                {
                    "partner_id": self.partner_a.id,
                }
            )
        )
        purchase_order.onchange_partner_id()
        PurchaseOrderLine = self.env["purchase.order.line"].with_context(
            tracking_disable=True
        )
        PurchaseOrderLine.sudo().create(
            {
                "name": self.product_order.name,
                "product_id": self.product_order.id,
                "product_qty": 10.0,
                "product_uom": self.product_order.uom_id.id,
                "price_unit": self.product_order.list_price,
                "order_id": purchase_order.id,
                "taxes_id": False,
            }
        )

        self.partner_a.write({"purchase_note": False})

        self.env["ir.config_parameter"].set_param("purchase.use_purchase_note", "Test")

        purchase_order.onchange_partner_id()

    def test_parent_terms(self):

        purchase_order = (
            self.env["purchase.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_3.id,
                }
            )
        )
        purchase_order.onchange_partner_id()
        self.assertIn("Partner", str(purchase_order.notes))

        purchase_order.write({"partner_id": self.partner_4.id})
        purchase_order.onchange_partner_id()
        self.assertIn("Partner4", str(purchase_order.notes))

    def test_clean_after_change(self):

        purchase_order = (
            self.env["purchase.order"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "partner_id": self.partner_3.id,
                }
            )
        )
        purchase_order.onchange_partner_id()
        self.assertIn("Partner", str(purchase_order.notes))
        self.env["ir.config_parameter"].set_param("purchase.use_purchase_note", False)

        self.partner_a.write({"purchase_note": False})
        purchase_order.write({"partner_id": self.partner_a.id})
        purchase_order.onchange_partner_id()
        self.assertFalse(purchase_order.notes)
