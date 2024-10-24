# Copyright 2023 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestPurchaseOrderOwner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.product_id = cls.env.ref("product.product_product_9")
        cls.uom_id = cls.env.ref("uom.product_uom_unit")

        # Owner
        cls.owner_id = cls.env["res.partner"].create({"name": "Owner test"})

    def test_purchase_order_owner(self):
        """Create a purchase order
        Set owner_id on purchase
        Check owner_id is set in corresponding incoming picking
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_id.id,
                "owner_id": self.owner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id.name,
                            "product_id": self.product_id.id,
                            "product_qty": 1.0,
                            "product_uom": self.uom_id.id,
                            "price_unit": 100.0,
                            "date_planned": datetime.today(),
                        },
                    )
                ],
            }
        )
        po.button_confirm()
        picking_id = po.picking_ids
        self.assertEqual(picking_id.owner_id, self.owner_id)
