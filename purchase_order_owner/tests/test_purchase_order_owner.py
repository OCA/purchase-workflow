# Copyright 2023 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestPurchaseOrderOwner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env["res.partner"].create({"name": "Partner 1"})
        self.product_id = self.env["product.product"].create(
            {"name": "Desk Combination", "type": "consu", "purchase_method": "purchase"}
        )
        self.uom_id = self.env["uom.uom"].create({"name": "Units"})

        # Owner
        self.owner_id = self.env["res.partner"].create({"name": "Owner test"})

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
                            "product_uom_id": self.uom_id.id,
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
