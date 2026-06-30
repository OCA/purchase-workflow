# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _has_discrete_product_uom_reference(self) -> bool:
        """Return whether the line UoM is based on the Unit(s) reference.

        :return: whether ``product_uom_id`` represents a discrete/countable UoM.
        """
        self.ensure_one()
        unit_uom = self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        if not unit_uom or not self.product_uom_id:
            return False
        return self.product_uom_id._has_common_reference(unit_uom)

    def _round_qty_to_discrete_uom(self) -> float:
        """Round the purchase quantity UP to a whole line UoM quantity.

        :return: rounded ``product_qty``.
        """
        self.ensure_one()
        return fields.Float.round(
            self.product_qty or 0.0,
            precision_rounding=1.0,
            rounding_method="UP",
        )

    @api.onchange("product_qty", "product_uom_id", "display_type")
    def _onchange_product_qty_round_discrete_uom(self):
        """Round countable purchase quantities to the next whole number."""
        for line in self:
            if line.display_type or not line.product_uom_id:
                continue

            qty_to_order = line.product_qty or 0.0
            if line.product_uom_id.compare(qty_to_order, 0.0) <= 0:
                continue
            if not line._has_discrete_product_uom_reference():
                continue

            rounded_qty = line._round_qty_to_discrete_uom()
            if line.product_uom_id.compare(rounded_qty, qty_to_order) != 0:
                line.product_qty = rounded_qty
