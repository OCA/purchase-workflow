# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchasePackaging(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line_obj = cls.env["purchase.order.line"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_ok": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.partner.id,
                            "min_qty": 1,
                            "price": 10.0,
                        }
                    )
                ],
            }
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.packaging_uom = cls.env["uom.uom"].create(
            {
                "name": "Box of 6",
                "relative_uom_id": cls.uom_unit.id,
                "relative_factor": 6.0,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)

    def test_purchase_packaging_from_procurement(self):
        """Test if packaging UoM is passed from procurement to PO line"""
        values = {
            "warehouse_id": self.warehouse,
            "packaging_uom_id": self.packaging_uom,
            "route_ids": self.warehouse.reception_route_id,
        }
        self.env["stock.rule"].run(
            [
                self.env["stock.rule"].Procurement(
                    self.product,
                    12.0,
                    self.uom_unit,
                    self.warehouse.lot_stock_id,
                    "Test procurement",
                    "TEST_PROC",
                    self.env.company,
                    values,
                )
            ]
        )
        po_line = self.line_obj.search(
            [
                ("product_id", "=", self.product.id),
                ("order_id.origin", "ilike", "TEST_PROC"),
            ]
        )
        self.assertTrue(po_line, "PO line should have been created")
        self.assertEqual(po_line.product_uom_id, self.packaging_uom)
        self.assertEqual(po_line.product_qty, 2.0)

    def test_purchase_packaging_from_move(self):
        """Test if packaging UoM is passed from stock move to procurement to PO line"""
        buy_route = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.product.route_ids = [Command.link(buy_route.id)]
        move = self.env["stock.move"].create(
            {
                "origin": "TEST_MOVE_ORIGIN",
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 18.0,
                "product_uom": self.uom_unit.id,
                "procure_method": "make_to_order",
            }
        )
        move.packaging_uom_id = self.packaging_uom
        move._action_confirm()
        po_line = self.line_obj.search(
            [
                ("product_id", "=", self.product.id),
                ("order_id.origin", "ilike", "TEST_MOVE_ORIGIN"),
            ]
        )

        self.assertTrue(po_line, "PO line should have been created from move")
        self.assertEqual(po_line.product_uom_id, self.packaging_uom)
        self.assertEqual(po_line.product_qty, 3.0)  # 18 / 6
