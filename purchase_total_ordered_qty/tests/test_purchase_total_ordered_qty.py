# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from json import dumps

from odoo.tests import TransactionCase


class TestPurchaseTotalOrderedQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.uom_cubic_meter = cls.env.ref("uom.product_uom_cubic_meter")
        cls.uom_litre = cls.env.ref("uom.product_uom_litre")
        cls.partner = cls.env["res.partner"].create({"name": "Partner 1"})
        cls.product1, cls.product2, cls.product3 = cls.env["product.product"].create(
            [
                {
                    "name": "Product 1",
                    "uom_id": cls.uom_unit.id,
                    "uom_po_id": cls.uom_unit.id,
                },
                {
                    "name": "Product 2",
                    "uom_id": cls.uom_dozen.id,
                    "uom_po_id": cls.uom_dozen.id,
                },
                {
                    "name": "Product 3",
                    "uom_id": cls.uom_cubic_meter.id,
                    "uom_po_id": cls.uom_cubic_meter.id,
                },
            ]
        )
        cls.order_vals = {
            "partner_id": cls.partner.id,
            "company_id": cls.env.user.company_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product1.name,
                        "product_id": cls.product1.id,
                        "product_qty": 10.0,
                        "product_uom": cls.product1.uom_po_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product2.name,
                        "product_id": cls.product2.id,
                        "product_qty": 1.0,
                        "product_uom": cls.product2.uom_po_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product3.name,
                        "product_id": cls.product3.id,
                        "product_qty": 0.05,
                        "product_uom": cls.product3.uom_po_id.id,
                    },
                ),
            ],
        }

    def test_00_total_ordered_qty(self):
        order = self.env["purchase.order"].create(self.order_vals)
        self.assertEqual(
            order.total_ordered_qty_json,
            dumps({self.uom_unit.id: 22.0, self.uom_litre.id: 50.0}),
        )
        self.assertEqual(order.total_ordered_qty_text, "50.0 L\n22.0 Units")
