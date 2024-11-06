# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _propagage_qty_to_moves(self):
        kit_purchase_lines = self.env["purchase.order.line"].browse()
        for line in self:
            if line.state != "purchase":
                continue
            kit_line = line._propagate_qty_to_moves_mrp()
            if kit_line:
                kit_purchase_lines |= line
        super(PurchaseOrderLine, self - kit_purchase_lines)._propagage_qty_to_moves()

    def _propagate_qty_to_moves_mrp(self):
        self.ensure_one()
        relevant_bom = False
        for bom in self.move_ids.bom_line_id.bom_id:
            if bom.type != "phantom":
                continue
            if (
                bom.product_id == self.product_id
                or bom.product_tmpl_id == self.product_id.product_tmpl_id
                and not bom.product_id
            ):
                relevant_bom = bom
                break
        if not relevant_bom:
            relevant_bom = (
                self.env["mrp.bom"]
                .sudo()
                ._bom_find(product=self.product_id, bom_type="phantom")
            )
        if not relevant_bom:
            return None
        new_kit_quantity = self.product_uom_qty
        boms, bom_sub_lines = relevant_bom.explode(self.product_id, new_kit_quantity)
        for bom_line, bom_line_data in bom_sub_lines:
            bom_line_uom = bom_line.product_uom_id
            quant_uom = bom_line.product_id.uom_id
            new_component_qty, procurement_uom = bom_line_uom._adjust_uom_quantities(
                bom_line_data["qty"], quant_uom
            )
            moves = self.move_ids.filtered(
                lambda move: move.bom_line_id == bom_line and move.state != "cancel"
            )
            previous_component_qty = sum(moves.mapped("product_uom_qty"))
            removable_qty = moves._get_removable_qty()
            quantity_to_remove = previous_component_qty - new_component_qty
            if (
                float_compare(
                    removable_qty,
                    quantity_to_remove,
                    precision_rounding=procurement_uom.rounding,
                )
                >= 0
            ):
                moves._deduce_qty(quantity_to_remove, procurement_uom.id)
            else:
                raise UserError(
                    _(
                        "You cannot remove more that what remains to be done. "
                        "For the kit %s.",
                        bom_line.product_id.name,
                    )
                )
        return self
