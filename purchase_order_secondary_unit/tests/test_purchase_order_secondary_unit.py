# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseOrderSecondaryUnit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.product.purchase_secondary_uom_id = cls.secondary_unit.id
        cls.partner = cls.env["res.partner"].create(
            {"name": "test - partner", "supplier": True}
        )
        type_obj = cls.env["stock.picking.type"]
        company_id = cls.env.user.company_id.id
        picking_type_id = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)],
            limit=1,
        )
        if not picking_type_id:
            picking_type_id = cls.env.ref("stock.picking_type_in")
        cls.purchase_order_obj = cls.env["purchase.order"]
        po_val = {
            "partner_id": cls.partner.id,
            "company_id": cls.env.user.company_id.id,
            "picking_type_id": picking_type_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product.name,
                        "product_id": cls.product.id,
                        "product_qty": 1,
                        "product_uom": cls.product.uom_id.id,
                        "price_unit": 1000.00,
                        "date_planned": fields.Datetime.now(),
                    },
                )
            ],
        }
        po = cls.purchase_order_obj.new(po_val)
        po.onchange_partner_id()
        cls.order = cls.purchase_order_obj.create(po_val)

    def test_onchange_secondary_uom(self):
        self.order.order_line.write(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
        self.order.order_line._onchange_secondary_uom()
        self.assertEqual(self.order.order_line.product_qty, 3.5)

    def test_onchange_product_qty_purchase_order_secondary_unit(self):
        self.order.order_line.update(
            {"secondary_uom_id": self.secondary_unit.id, "product_qty": 3.5}
        )
        self.order.order_line._onchange_product_qty_purchase_order_secondary_unit()
        self.assertEqual(self.order.order_line.secondary_uom_qty, 5.0)

    def test_default_secondary_unit(self):
        self.order.order_line._onchange_product_id_purchase_order_secondary_unit()
        self.assertEqual(self.order.order_line.secondary_uom_id, self.secondary_unit)

    def test_onchange_order_product_uom(self):
        self.order.order_line.update(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom": self.product_uom_gram.id,
                "product_qty": 3500.00,
            }
        )
        self.order.order_line._onchange_product_uom_purchase_order_secondary_unit()
        self.assertEqual(self.order.order_line.secondary_uom_qty, 5.0)
