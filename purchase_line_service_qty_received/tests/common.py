# Copyright 2024 Raumschmiede GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestServiceQtyReceivedCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {"name": "Stockable", "type": "product", "purchase_method": "receive"}
        )
        cls.reception = cls.product.create(
            {"name": "Service", "type": "service", "purchase_method": "receive"}
        )

        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier for Service Products",
            }
        )

    def _new_purchase_order(self):
        warehouse = self.env.ref("stock.warehouse0")
        self.env["stock.quant"]._update_available_quantity(
            self.product, warehouse.lot_stock_id, 10
        )
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.reception.id,
                            "product_uom_qty": 1,
                            "product_uom": self.reception.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )

    def _check_qty_received(self, sum_qty_received):
        self.po.flush()
        self.po.order_line.flush()
        self.assertEqual(
            sum(self.po.order_line.mapped("qty_received")), sum_qty_received
        )

    def _receive_order(self):
        pick = self.po.picking_ids
        pick.move_lines.write({"quantity_done": 1})
        pick.button_validate()

    def _return_order(self):
        # Create return picking
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.po.picking_ids.ids,
                active_id=self.po.picking_ids.id,
                active_model="stock.picking",
            )
        )
        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity = 1.0
        return_wiz.product_return_moves.to_refund = True
        res = return_wiz.create_returns()
        return_pick = self.env["stock.picking"].browse(res["res_id"])

        # Validate picking
        return_pick.move_lines.write({"quantity_done": 1})
        return_pick.button_validate()
