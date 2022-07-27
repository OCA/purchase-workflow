# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo.tests.common import TransactionCase


class TestSaleMrpFlow(TransactionCase):
    def setUp(self):
        super().setUp()
        self.categ_id = self.env.ref("product.product_category_all")
        self.categ_id.property_cost_method = "average"
        # Creating all components
        self.component_a = self._create_product("Comp A")
        self.component_b = self._create_product("Comp B")
        self.component_c = self._create_product("Comp C")
        # kit_1 --|- component_a   x2
        #         |- component_b   x1
        #         |- component_c   x3
        self.kit_1 = self._create_product("Kit 1")
        self.bom_kit_1 = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.kit_1.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "phantom",
                "bom_line_ids": [
                    (0, 0, {"product_id": self.component_a.id, "product_qty": 2}),
                    (0, 0, {"product_id": self.component_b.id, "product_qty": 1}),
                    (0, 0, {"product_id": self.component_c.id, "product_qty": 3}),
                ],
            }
        )
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "Partner 1"}).id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.kit_1.id,
                            "product_uom": self.kit_1.uom_id.id,
                            "name": self.kit_1.name,
                            "price_unit": 100,
                            "product_qty": 1,
                            "date_planned": date.today(),
                        },
                    )
                ],
            }
        )
        self.po.button_confirm()
        for line in self.po.picking_ids.move_lines:
            line.write({"quantity_done": line.product_uom_qty})

    def _create_product(self, name):
        return self.env["product.product"].create(
            {"name": name, "type": "product", "categ_id": self.categ_id.id}
        )

    def _do_set_price_type_and_validate(self, valuation_price_type):
        self.bom_kit_1.valuation_price_type = valuation_price_type
        return self.po.picking_ids.button_validate()

    def _check_standard_price(self, result):
        for bom_line in self.bom_kit_1.bom_line_ids:
            self.assertAlmostEqual(
                bom_line.product_id.standard_price, result[bom_line.product_id.id]
            )

    def _check_validate_stock_picking_and_check_result(
        self, valuation_price_type, result
    ):
        """Test that the valuation by valuation_price_type method is working with kit"""
        self._do_set_price_type_and_validate(valuation_price_type)
        self._check_standard_price(result)

    def test_01_purchase_order_valuation_by_lines(self):
        result = {
            self.component_a.id: 16.67,
            self.component_b.id: 33.33,
            self.component_c.id: 11.11,
        }
        self._check_validate_stock_picking_and_check_result("by_lines", result)

    def test_02_purchase_order_valuation_by_quantities(self):
        result = {
            self.component_a.id: 16.67,
            self.component_b.id: 16.67,
            self.component_c.id: 16.67,
        }
        self._check_validate_stock_picking_and_check_result("by_quantities", result)

    def test_03_purchase_order_valuation_none(self):
        result = {
            self.component_a.id: 0,
            self.component_b.id: 0,
            self.component_c.id: 0,
        }
        self._check_validate_stock_picking_and_check_result("none", result)
