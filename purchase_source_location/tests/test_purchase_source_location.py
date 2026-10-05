# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.product.tests import common


class TestCreatePicking(common.TestProductCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env["res.partner"].create({"name": "Wood Corner Partner"})
        cls.product_id_1 = cls.env["product.product"].create({"name": "Large Desk"})
        cls.product_id_2 = cls.env["product.product"].create(
            {"name": "Conference Chair"}
        )

        cls.user_purchase_user = mail_new_test_user(
            cls.env,
            name="Pauline Poivraisselle",
            login="pauline",
            email="pur@example.com",
            notification_type="inbox",
            groups="purchase.group_purchase_user",
        )

        cls.po_vals = {
            "partner_id": cls.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_1.name,
                        "product_id": cls.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom": cls.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                )
            ],
        }

    def test_00_create_picking(self):
        # Manually set partner supplier location to custom one
        test_location = self.env["stock.location"].create(
            {
                "name": "Test Supplier Location",
                "usage": "supplier",
            }
        )
        self.partner_id.property_stock_supplier = test_location

        self.po = self.env["purchase.order"].create(self.po_vals)
        self.assertEqual(
            self.po.source_location_id,
            test_location,
            "Vendor Location should match partner's supplier location",
        )
        self.po.button_confirm()
        # Check picking's location_id was set from source_location_id
        picking = self.po.picking_ids[0]
        self.assertEqual(
            picking.location_id,
            test_location,
            "Picking should use custom vendor location from source_location_id",
        )
