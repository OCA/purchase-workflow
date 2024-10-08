# Copyright 2023 ArcheTI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseStockPickingNote(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseStockPickingNote, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
            }
        )
        product = cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
            }
        )
        cls.date_planned = "2023-06-10 12:00:00"
        cls.order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom": product.uom_id.id,
                            "name": product.display_name,
                            "date_planned": cls.date_planned,
                            "product_qty": 1,
                            "price_unit": product.standard_price,
                        },
                    )
                ],
            }
        )

    def test_01_purchase_to_picking_note(self):
        """Pass note to picking from PO"""
        self.order.picking_note = "This note goes to the picking..."
        self.order.button_confirm()
        self.assertEqual(self.order.picking_ids[:1].note, self.order.picking_note)
