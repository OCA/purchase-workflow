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

    def test_onchange_partner_id(self):

        purchase_order = (
            self.env["purchase.order"]
            .with_context(tracking_disable=True)
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
        PurchaseOrderLine.create(
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
