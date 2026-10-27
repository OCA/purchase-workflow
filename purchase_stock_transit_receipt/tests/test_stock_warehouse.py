# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon

from ..hooks import post_init_hook


class TestStockWarehouse(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Transit Warehouse", "code": "TWH"}
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "is_storable": True,
                "standard_price": 10.0,
            }
        )

    def _transit_rules(self, warehouse):
        return self.env["stock.rule"].search(
            [("location_src_id", "=", warehouse.incoming_transit_location_id.id)]
        )

    def _create_purchase(self, quantity=5.0):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.warehouse.transit_in_type_id.id,
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

    def _validate(self, picking):
        picking.action_assign()
        picking.move_ids.picked = True
        picking._action_done()

    def _next_picking(self, picking):
        return picking.move_ids.move_dest_ids.picking_id

    def assertTransitReceiptChain(self, warehouse):
        rule = self._transit_rules(warehouse)
        self.assertEqual(len(rule), 1)
        self.assertEqual(rule.route_id, warehouse.reception_route_id)
        self.assertEqual(rule.action, "push")
        self.assertEqual(rule.picking_type_id, warehouse.in_type_id)
        self.assertEqual(
            rule.location_dest_id, warehouse.in_type_id.default_location_dest_id
        )

    def test_new_warehouse(self):
        location = self.warehouse.incoming_transit_location_id
        self.assertEqual(location.name, "TWH: Incoming transit")
        self.assertEqual(location.usage, "transit")
        self.assertEqual(location.company_id, self.warehouse.company_id)
        self.assertEqual(
            location.location_id, self.env.ref("stock.stock_location_locations")
        )
        self.assertFalse(location.warehouse_id)
        picking_type = self.warehouse.transit_in_type_id
        self.assertEqual(picking_type.code, "incoming")
        self.assertEqual(picking_type.warehouse_id, self.warehouse)
        self.assertEqual(
            picking_type.default_location_src_id,
            self.env.ref("stock.stock_location_suppliers"),
        )
        self.assertEqual(picking_type.default_location_dest_id, location)
        self.assertEqual(picking_type.sequence_id.prefix, "TWH/TR/")
        self.assertEqual(
            picking_type.return_picking_type_id, self.warehouse.out_type_id
        )
        self.assertEqual(self.warehouse.reception_steps, "one_step")
        self.assertTransitReceiptChain(self.warehouse)

    def test_existing_warehouse(self):
        warehouse = self.warehouse
        self._transit_rules(warehouse).unlink()
        warehouse.transit_in_type_id.unlink()
        warehouse.incoming_transit_location_id.unlink()
        warehouse.reception_steps = "two_steps"
        post_init_hook(self.env)
        post_init_hook(self.env)
        self.assertEqual(warehouse.incoming_transit_location_id.usage, "transit")
        self.assertEqual(
            warehouse.transit_in_type_id.default_location_dest_id,
            warehouse.incoming_transit_location_id,
        )
        self.assertEqual(
            self.env["stock.picking.type"].search_count(
                [("warehouse_id", "=", warehouse.id), ("sequence_code", "=", "TR")]
            ),
            1,
        )
        self.assertEqual(warehouse.reception_steps, "two_steps")
        self.assertTransitReceiptChain(warehouse)

    def test_reception_steps_change(self):
        for steps in ("two_steps", "three_steps", "one_step", "two_steps"):
            self.warehouse.reception_steps = steps
            self.assertTransitReceiptChain(self.warehouse)

    def test_rename_warehouse_code(self):
        self.warehouse.code = "NWH"
        self.assertEqual(
            self.warehouse.incoming_transit_location_id.name, "NWH: Incoming transit"
        )
        self.assertEqual(
            self.warehouse.transit_in_type_id.sequence_id.prefix, "NWH/TR/"
        )

    def test_purchase_one_step(self):
        purchase = self._create_purchase()
        transit_receipt = purchase.picking_ids
        self.assertEqual(len(transit_receipt), 1)
        self.assertEqual(
            transit_receipt.location_dest_id,
            self.warehouse.incoming_transit_location_id,
        )
        self.assertFalse(transit_receipt.move_ids.move_dest_ids)
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self.assertEqual(physical_receipt.picking_type_id, self.warehouse.in_type_id)
        self.assertEqual(physical_receipt.state, "assigned")
        self.assertEqual(
            physical_receipt.location_id, self.warehouse.incoming_transit_location_id
        )
        self.assertEqual(physical_receipt.location_dest_id, self.warehouse.lot_stock_id)
        self.assertEqual(purchase.picking_ids, transit_receipt)
        self._validate(physical_receipt)
        self.assertEqual(
            self.product.with_context(warehouse_id=self.warehouse.id).qty_available,
            5.0,
        )

    def test_purchase_three_steps(self):
        self.warehouse.reception_steps = "three_steps"
        transit_receipt = self._create_purchase().picking_ids
        self._validate(transit_receipt)
        physical_receipt = self._next_picking(transit_receipt)
        self.assertEqual(physical_receipt.picking_type_id, self.warehouse.in_type_id)
        self.assertEqual(
            physical_receipt.location_dest_id, self.warehouse.wh_input_stock_loc_id
        )
        self._validate(physical_receipt)
        quality_control = self._next_picking(physical_receipt)
        self.assertEqual(quality_control.picking_type_id, self.warehouse.qc_type_id)
        self._validate(quality_control)
        storage = self._next_picking(quality_control)
        self.assertEqual(storage.picking_type_id, self.warehouse.store_type_id)
        self.assertEqual(storage.location_dest_id, self.warehouse.lot_stock_id)

    def test_goods_in_transit(self):
        transit_receipt = self._create_purchase().picking_ids
        self._validate(transit_receipt)
        location = self.warehouse.incoming_transit_location_id
        self.assertTrue(location._should_be_valued())
        self.assertEqual(
            sum(transit_receipt.move_ids.stock_valuation_layer_ids.mapped("value")),
            50.0,
        )
        self.assertEqual(
            self.product.with_context(location=location.id).qty_available, 5.0
        )
        self.assertEqual(
            self.product.with_context(warehouse_id=self.warehouse.id).qty_available,
            0.0,
        )
        delivery = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "partner_id": self.customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        }
                    )
                ],
            }
        )
        delivery.action_confirm()
        delivery.action_assign()
        self.assertEqual(delivery.state, "confirmed")
