# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleProcurementAmendment(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.sale_obj = cls.env["sale.order"]
        cls.sale_order_line_obj = cls.env["sale.order.line"]
        cls.purchase_order_line_obj = cls.env["purchase.order.line"]
        cls.supplier = cls.env.ref("base.res_partner_2")

        vals = {
            "name": "Product MTO",
            "seller_ids": [(0, 0, {"name": cls.supplier.id})],
        }
        cls.product_mto = cls.env["product.product"].create(vals)
        cls.wood_corner = cls.env.ref("base.res_partner_1")

        cls.mto_route = cls.warehouse.mto_pull_id.route_id
        cls.product_mto.route_ids |= cls.mto_route

        po = cls.env["purchase.order"].search(
            [("state", "=", "draft"), ("partner_id", "=", cls.supplier.id)]
        )

        po.button_cancel()

    def _create_sale_order(self):

        vals = {
            "partner_id": self.wood_corner.id,
        }
        self.order = self.sale_obj.create(vals)
        self.order.onchange_partner_id()
        vals = {
            "order_id": self.order.id,
            "product_id": self.product_mto.id,
            "product_uom_qty": 10.0,
        }
        self.sale_line = self.sale_order_line_obj.create(vals)
        self.sale_line.product_id_change()

    def test_00_sale_purchase_amend(self):
        """
        Test the picking_in_progress and can_be_amended values
        :return:
        """
        self._create_sale_order()
        self.order.order_line.route_id = self.mto_route
        self.order.action_confirm()
        lines = self.purchase_order_line_obj.search(
            [("move_dest_ids", "in", self.order.order_line.move_ids.ids)]
        )
        self.assertEqual(lines.product_uom_qty, self.order.order_line.product_uom_qty)
        self.order.order_line.write({"product_uom_qty": 9.0})
        lines = self.purchase_order_line_obj.search(
            [("move_dest_ids", "in", self.order.order_line.move_ids.ids)]
        )
        self.assertEqual(lines.product_uom_qty, self.order.order_line.product_uom_qty)
        lines.order_id.button_confirm()
        with self.assertRaises(ValidationError):
            self.order.order_line.write({"product_uom_qty": 8.0})
