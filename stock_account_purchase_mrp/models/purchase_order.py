# Copyright 2022 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - César A. Sánchez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_bom_component_qty(self, bom):
        bom_quantity = self.product_id.uom_id._compute_quantity(
            1, bom.product_uom_id, rounding_method="HALF-UP"
        )
        boms, lines = bom.explode(self.product_id, bom_quantity)
        components = {}
        for line, line_data in lines:
            product = line.product_id.id
            uom = line.product_uom_id
            qty = line_data["qty"]
            if components.get(product, False):
                if uom.id != components[product]["uom"]:
                    from_uom = uom
                    to_uom = self.env["uom.uom"].browse(components[product]["uom"])
                    qty = from_uom._compute_quantity(qty, to_uom)
                components[product]["qty"] += qty
            else:
                # To be in the uom reference of the product
                to_uom = self.env["product.product"].browse(product).uom_id
                if uom.id != to_uom.id:
                    from_uom = uom
                    qty = from_uom._compute_quantity(qty, to_uom)
                components[product] = {"qty": qty, "uom": to_uom.id}
        return components
