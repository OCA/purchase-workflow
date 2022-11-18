# Copyright 2020 Jarsa Sistemas
# Copyright 2021 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

from odoo.tests import Form, SavepointCase

_logger = logging.getLogger(__name__)


class TestPurchaseStockSecondaryUnit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Active multiple units of measure security group for user
        cls.env.user.groups_id = [(4, cls.env.ref("uom.group_uom").id)]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.ProductSecondaryUnit = cls.env["product.secondary.unit"]
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        with Form(cls.env["product.product"]) as product_form:
            product_form.name = "Test"
            product_form.type = "product"
            with product_form.secondary_uom_ids.new() as secondary_uom:
                secondary_uom.name = "box"
                secondary_uom.uom_id = cls.product_uom_unit
                secondary_uom.factor = 5.0
        cls.product = product_form.save()
        cls.secondary_product_uom = cls.product.secondary_uom_ids[:1]
        po = cls.env["purchase.order"].new({"partner_id": cls.partner.id})
        po.onchange_partner_id()
        cls.purchase_order = cls.env["purchase.order"].create(
            po._convert_to_write(po._cache)
        )
        with Form(cls.purchase_order) as po_form:
            po_form.partner_id = cls.partner
            po_form.company_id = cls.env.company
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
        self.assertEqual(picking.move_lines.secondary_uom_qty, 0.0)
        self.assertFalse(picking.move_lines.secondary_uom_id)
        self.assertEqual(picking.move_lines.product_uom_qty, 10.0)

    def test_confirm_new_purchase_order(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        self.assertEqual(picking.move_lines.secondary_uom_qty, 2.0)
        self.assertEqual(
            picking.move_lines.secondary_uom_id, self.secondary_product_uom
        )
        self.assertEqual(picking.move_lines.product_uom_qty, 10.0)

    def test_update_confirmed_purchase_order(self):
        self.purchase_order.button_confirm()
        with Form(self.purchase_order) as po_form:
            with po_form.order_line.edit(0) as line:
                line.secondary_uom_qty = 5.0
        picking = self.purchase_order.picking_ids
        self.assertEqual(picking.move_lines.secondary_uom_qty, 5.0)
        self.assertEqual(
            picking.move_lines.secondary_uom_id, self.secondary_product_uom
        )
        self.assertEqual(picking.move_lines.product_uom_qty, 25.0)

    def test_update_confirmed_purchase_order_with_move_validated(self):
        self.purchase_order.button_confirm()
        picking = self.purchase_order.picking_ids
        picking.action_assign()
        picking.move_line_ids.qty_done = picking.move_lines.product_uom_qty
        picking.button_validate()
        with Form(self.purchase_order) as po_form:
            with po_form.order_line.edit(0) as line:
                line.secondary_uom_qty = 5.0
        picking = self.purchase_order.picking_ids.filtered(lambda p: p.state != "done")
        self.assertEqual(picking.move_lines.secondary_uom_qty, 3.0)
        self.assertEqual(
            picking.move_lines.secondary_uom_id, self.secondary_product_uom
        )
        self.assertEqual(picking.move_lines.product_uom_qty, 15.0)
        # Assigned move line
        self.assertEqual(picking.move_line_ids.secondary_uom_qty, 3.0)
        self.assertEqual(
            picking.move_line_ids.secondary_uom_id, self.secondary_product_uom
        )
        self.assertEqual(picking.move_line_ids.product_uom_qty, 15.0)
