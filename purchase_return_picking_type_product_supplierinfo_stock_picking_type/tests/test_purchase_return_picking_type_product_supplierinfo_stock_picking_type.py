# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseReturnPickingTypeProductSupplierinfoStockPickingType(BaseCommon):
    def setUp(self):
        super().setUpClass()
        self.warehouse = self.env.ref("stock.warehouse0")
        self.supplier = self.env["res.partner"].create({"name": "Supplier"})
        self.picking_in_a = self.env["stock.picking.type"].create(
            {
                "name": "Incoming A",
                "code": "incoming",
                "sequence_code": "IN-A",
                "warehouse_id": self.warehouse.id,
            }
        )
        self.picking_in_b = self.env["stock.picking.type"].create(
            {
                "name": "Incoming B",
                "code": "incoming",
                "sequence_code": "IN-B",
                "warehouse_id": self.warehouse.id,
            }
        )
        self.picking_in_c = self.env["stock.picking.type"].create(
            {
                "name": "Incoming C",
                "code": "incoming",
                "sequence_code": "IN-C",
                "warehouse_id": self.warehouse.id,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "min_qty": 1,
                            "price": 5,
                            "picking_type_id": self.picking_in_a.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "min_qty": 1,
                            "price": 10,
                            "picking_type_id": self.picking_in_b.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self.supplier.id,
                            "min_qty": 1,
                            "price": 20,
                        },
                    ),
                ],
            }
        )

    def _create_purchase_return_order(self, picking_type_id):
        order_form = Form(self.env["purchase.return.order"])
        order_form.partner_id = self.supplier
        order_form.picking_type_id = picking_type_id
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_qty = 1
        return order_form.save()

    def test_product_picking_type_a(self):
        pro = self._create_purchase_return_order(self.picking_in_a)
        self.assertEqual(pro.order_line.price_unit, 5)

    def test_product_picking_type_b(self):
        pro = self._create_purchase_return_order(self.picking_in_b)
        self.assertEqual(pro.order_line.price_unit, 10)

    def test_product_picking_type_c(self):
        pro = self._create_purchase_return_order(self.picking_in_c)
        self.assertEqual(pro.order_line.price_unit, 20)
        pro.picking_type_id = self.picking_in_a
        pro.onchange_picking_type_id()
        self.assertEqual(pro.order_line.price_unit, 5)
