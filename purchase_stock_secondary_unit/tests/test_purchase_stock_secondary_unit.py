# Copyright 2020 Jarsa Sistemas
# Copyright 2021 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseStockSecondaryUnit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Active multiple units of measure security group for user
        cls.env.user.group_ids = [(4, cls.env.ref("uom.group_uom").id)]
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.ProductSecondaryUnit = cls.env["product.secondary.unit"]
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        with Form(cls.env["product.product"]) as product_form:
            product_form.name = "Test"
            with product_form.secondary_uom_ids.new() as secondary_uom:
                secondary_uom.name = "box"
                secondary_uom.uom_id = cls.product_uom_unit
                secondary_uom.factor = 5.0
        cls.product = product_form.save()
        cls.secondary_product_uom = cls.product.secondary_uom_ids[:1]
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.warehouse.in_type_id.id,
            }
        )
        with Form(cls.purchase_order) as po_form:
            po_form.partner_id = cls.partner
            with po_form.order_line.new() as line:
                line.product_id = cls.product
                line.secondary_uom_id = cls.secondary_product_uom
                line.secondary_uom_qty = 2.0
        cls.purchase_order = po_form.save()

    def test_confirm_purchase_order_without_secondary_uom(self):
        with Form(self.purchase_order) as po_form:
            with po_form.order_line.edit(0) as line:
                line.secondary_uom_id = self.ProductSecondaryUnit.browse()
                line.secondary_uom_qty = 0.0
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        self.assertEqual(picking.move_ids.secondary_uom_qty, 0.0)
        self.assertFalse(picking.move_ids.secondary_uom_id)
        self.assertEqual(picking.move_ids.product_uom_qty, 10.0)

    def test_confirm_new_purchase_order(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        self.assertEqual(picking.move_ids.secondary_uom_qty, 2.0)
        self.assertEqual(picking.move_ids.secondary_uom_id, self.secondary_product_uom)
        self.assertEqual(picking.move_ids.product_uom_qty, 10.0)

    def test_update_confirmed_purchase_order(self):
        self.purchase_order.button_confirm()
        # Other addons may make confirmed orders readonly in the form view.
        # Exercise the line update independently of those UI restrictions.
        self.purchase_order.order_line.write(
            {"secondary_uom_qty": 5.0, "product_qty": 25.0}
        )
        picking = self.purchase_order.picking_ids
        self.assertEqual(picking.move_ids.secondary_uom_qty, 5.0)
        self.assertEqual(picking.move_ids.secondary_uom_id, self.secondary_product_uom)
        self.assertEqual(picking.move_ids.product_uom_qty, 25.0)

    def test_update_confirmed_purchase_order_with_move_validated(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.quantity = picking.move_ids.product_uom_qty
        picking.button_validate()
        # Other addons may make confirmed orders readonly in the form view.
        # Exercise the line update independently of those UI restrictions.
        self.purchase_order.order_line.write(
            {"secondary_uom_qty": 5.0, "product_qty": 25.0}
        )
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        self.assertEqual(picking.move_ids.secondary_uom_qty, 3.0)
        self.assertEqual(picking.move_ids.secondary_uom_id, self.secondary_product_uom)
        self.assertEqual(picking.move_ids.product_uom_qty, 15.0)
        # Assigned move line
        self.assertEqual(picking.move_line_ids.secondary_uom_qty, 3.0)
        self.assertEqual(
            picking.move_line_ids.secondary_uom_id, self.secondary_product_uom
        )
        self.assertEqual(picking.move_line_ids.quantity_product_uom, 15.0)

    def test_prepare_incremental_stock_move(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        picking.move_ids.quantity = 10.0
        picking.button_validate()
        line = self.purchase_order.order_line
        vals = line._prepare_stock_move_vals(
            picking, line.price_unit, 15.0, self.product.uom_id
        )
        self.assertEqual(vals["product_uom_qty"], 15.0)
        self.assertEqual(vals["secondary_uom_qty"], 3.0)

    def test_prepare_split_stock_moves(self):
        line = self.purchase_order.order_line
        picking = self.env["stock.picking"].create(
            self.purchase_order._prepare_picking()
        )
        destination = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.partner.property_stock_customer.id,
            }
        )
        line.move_dest_ids = destination
        vals = line._prepare_stock_moves(picking)
        self.assertEqual(len(vals), 2)
        for move_vals in vals:
            self.assertEqual(move_vals["product_uom_qty"], 5.0)
            self.assertEqual(move_vals["secondary_uom_qty"], 1.0)
            self.assertEqual(
                move_vals["secondary_uom_id"], self.secondary_product_uom.id
            )

    def test_service_does_not_create_stock_move(self):
        self.product.type = "service"
        self.purchase_order.button_confirm()
        self.assertFalse(self.purchase_order.picking_ids)

    def test_independent_secondary_quantity(self):
        self.secondary_product_uom.dependency_type = "independent"
        line = self.purchase_order.order_line
        line.write({"product_qty": 10.0, "secondary_uom_qty": 7.0})
        self.purchase_order.button_confirm()
        move = self.purchase_order.picking_ids.move_ids
        self.assertEqual(move.secondary_uom_qty, 7.0)
        self.assertEqual(move.product_uom_qty, 10.0)
        line.secondary_uom_qty = 9.0
        self.assertEqual(move.secondary_uom_qty, 9.0)
        self.assertEqual(move.product_uom_qty, 10.0)

    def test_procurement_secondary_values(self):
        line_model = self.env["purchase.order.line"]
        supplier = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 10.0,
            }
        )
        values = {
            "supplier": supplier,
            "date_planned": self.purchase_order.date_order,
            "secondary_uom_id": self.secondary_product_uom.id,
            "secondary_uom_qty": 2.0,
        }
        vals = line_model._prepare_purchase_order_line_from_procurement(
            self.product,
            10.0,
            self.product.uom_id,
            self.warehouse.lot_stock_id,
            self.product.name,
            "test",
            self.env.company,
            values,
            self.purchase_order,
        )
        self.assertEqual(vals["secondary_uom_id"], self.secondary_product_uom.id)
        self.assertEqual(vals["secondary_uom_qty"], 2.0)
        values.pop("secondary_uom_id")
        values.pop("secondary_uom_qty")
        vals = line_model._prepare_purchase_order_line_from_procurement(
            self.product,
            10.0,
            self.product.uom_id,
            self.warehouse.lot_stock_id,
            self.product.name,
            "test",
            self.env.company,
            values,
            self.purchase_order,
        )
        self.assertFalse(vals["secondary_uom_id"])
        self.assertEqual(vals["secondary_uom_qty"], 0.0)

    def test_stock_move_in_different_unit(self):
        picking = self.env["stock.picking"].create(
            self.purchase_order._prepare_picking()
        )
        dozen = self.env["uom.uom"].create(
            {
                "name": "Test dozen",
                "relative_uom_id": self.product.uom_id.id,
                "relative_factor": 12.0,
            }
        )
        vals = self.purchase_order.order_line._prepare_stock_move_vals(
            picking, 10.0, 2.0, dozen
        )
        self.assertEqual(vals["product_uom_qty"], 2.0)
        self.assertEqual(vals["secondary_uom_qty"], 4.8)

    def test_partial_receipt_and_backorder(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        picking.move_ids.quantity = 5.0
        picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(picking.state, "done")
        backorder = self.purchase_order.picking_ids - picking
        self.assertEqual(len(backorder), 1)
        self.assertEqual(backorder.move_ids.product_uom_qty, 5.0)
        self.assertEqual(backorder.move_ids.secondary_uom_qty, 1.0)
        self.assertEqual(
            backorder.move_ids.secondary_uom_id, self.secondary_product_uom
        )
        backorder.move_ids.quantity = 5.0
        backorder.button_validate()
        self.assertEqual(self.purchase_order.order_line.qty_received, 10.0)

    def test_cancelled_move_is_not_updated(self):
        self.secondary_product_uom.dependency_type = "independent"
        self.purchase_order.button_confirm()
        move = self.purchase_order.picking_ids.move_ids
        move._action_cancel()
        self.purchase_order.order_line.secondary_uom_qty = 8.0
        self.assertEqual(move.state, "cancel")
        self.assertEqual(move.secondary_uom_qty, 2.0)

    def test_storable_product_receipt(self):
        self.product.is_storable = True
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        picking.move_ids.quantity = 10.0
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(picking.move_ids.secondary_uom_qty, 2.0)
        self.assertEqual(self.product.qty_available, 10.0)
