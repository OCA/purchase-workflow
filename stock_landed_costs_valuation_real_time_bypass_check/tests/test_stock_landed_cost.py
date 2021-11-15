# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form, common


class TestStockLandedCost(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        category = cls.env["product.category"].create(
            {"name": "AVCO", "property_cost_method": "average"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test AVCO", "type": "product", "categ_id": category.id}
        )
        cls.product_lc = cls.env["product.product"].create(
            {"name": "Test LC", "landed_cost_ok": True}
        )
        cls.purchase_order = cls._create_purchase_order(cls)
        cls.picking = fields.first(cls.purchase_order.picking_ids)

    def _create_purchase_order(self):
        purchase = Form(self.env["purchase.order"])
        purchase.partner_id = self.partner
        with purchase.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.price_unit = 4
        order = purchase.save()
        order.button_confirm()
        picking = fields.first(order.picking_ids)
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()
        return order

    def _create_stock_landed_cost(self, price):
        lc = Form(self.env["stock.landed.cost"])
        lc.picking_ids.add(self.picking)
        with lc.cost_lines.new() as line_form:
            line_form.product_id = self.product_lc
            line_form.price_unit = price
        return lc.save()

    def _test_slc(self, lc, initial_cost, increase):
        final_cost = initial_cost + increase
        lc.button_validate()
        self.assertFalse(lc.account_move_id)
        line = lc.valuation_adjustment_lines.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(line.former_cost, initial_cost)
        self.assertEqual(line.additional_landed_cost, increase)
        self.assertEqual(line.final_cost, final_cost)
        svl_line = lc.stock_valuation_layer_ids.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(svl_line.value, increase)
        self.assertEqual(self.product.standard_price, final_cost)
        self.assertEqual(
            sum(self.product.stock_valuation_layer_ids.mapped("value")), final_cost
        )

    def test_slc(self):
        lc_1 = self._create_stock_landed_cost(6)
        self._test_slc(lc_1, 4, 6)
        # New LC
        lc_2 = self._create_stock_landed_cost(5)
        self._test_slc(lc_2, 10, 5)
