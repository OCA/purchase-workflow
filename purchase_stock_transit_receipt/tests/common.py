# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TransitReceiptCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Transit Warehouse", "code": "TWH"}
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "is_storable": True,
                "standard_price": 10.0,
            }
        )

    def _create_purchase(self, picking_type=None, quantity=5.0):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": (
                    picking_type or self.warehouse.transit_in_type_id
                ).id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": quantity,
                            "price_unit": 10.0,
                        }
                    )
                ],
            }
        )
        purchase.button_confirm()
        return purchase

    def _validate(self, picking, quantity=None):
        picking.action_assign()
        if quantity is not None:
            picking.move_ids.quantity = quantity
        picking.move_ids.picked = True
        picking._action_done()

    def _next_picking(self, picking):
        return picking.move_ids.move_dest_ids.picking_id
