# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common


class TestPurchaseOrderLineDescriptionPicking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        po_model = cls.env["purchase.order"]
        cls.po_line_model = cls.env["purchase.order.line"]
        cls.product_obj = cls.env["product.product"]
        cls.product_1 = cls.product_obj.create(
            {"name": "Test product 1", "default_code": "CDE", "standard_price": 7.5}
        )
        cls.product_2 = cls.product_obj.create(
            {"name": "Test product 2", "default_code": "BCD", "standard_price": 7.3}
        )
        supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.po = po_model.create({"partner_id": supplier.id})
        cls.po_line_1 = cls.po_line_model.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product_1.id,
                "date_planned": "2022-11-01",
                "name": "Description 1",
                "product_qty": 3.0,
                "product_uom": cls.product_1.uom_id.id,
                "price_unit": 10.0,
            }
        )
        cls.po_line_2 = cls.po_line_model.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product_2.id,
                "date_planned": "2022-11-05",
                "name": "Description 2",
                "product_qty": 4.0,
                "product_uom": cls.product_2.uom_id.id,
                "price_unit": 6.0,
            }
        )

    def test_description_picking(self):
        self.po.button_confirm()
        for line in self.po.order_line:
            self.assertEqual(len(line.move_ids), 1)
            self.assertEqual(line.name, line.move_ids.description_picking)
