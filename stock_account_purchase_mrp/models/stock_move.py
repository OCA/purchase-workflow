# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - César A. Sánchez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """ Returns the unit price for the move when it is a KIT
         according to the valuation_price_type"""
        self.ensure_one()
        # Only on stock move with purchase order line
        bom = (
            self.purchase_line_id
            and self.env["mrp.bom"]._bom_find(
                product=self.purchase_line_id.product_id,
                company_id=self.purchase_line_id.company_id.id,
                bom_type="phantom",
            )
            or False
        )
        result = super()._get_price_unit()
        if not bom:
            return result
        components_qty = self.purchase_line_id._get_bom_component_qty(bom)
        qty_all = sum(comp["qty"] for comp in components_qty.values())
        price_unit = result
        # if valuation_price_type is 'None' price_unit is the std one.
        if self.product_id.id in components_qty:
            if bom.valuation_price_type == "by_quantities":
                price_unit = self.purchase_line_id.price_unit / qty_all
            elif bom.valuation_price_type == "by_lines":
                price_unit = (
                    self.purchase_line_id.price_unit
                    / len(components_qty)
                    / components_qty[self.product_id.id]["qty"]
                )
        return price_unit
