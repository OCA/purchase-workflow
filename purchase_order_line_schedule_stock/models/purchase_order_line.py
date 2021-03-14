# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        new_vals = []
        vals = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        schedule_line_id = self.env.context.get("schedule_line_id", False)

        for val in vals:
            if "purchase_line_id" in val:
                pol = self.browse(val["purchase_line_id"])
                schedule_lines = pol.schedule_line_ids
                if schedule_line_id:
                    schedule_lines = pol.schedule_line_ids.filtered(
                        lambda l: l.id == schedule_line_id
                    )
                if not schedule_lines:
                    new_vals.append(val)
                    continue
                po_line_uom = self.product_uom
                quant_uom = pol.product_id.uom_id
                for sl in schedule_lines:
                    new_val = val.copy()
                    remaining_qty = sl.product_qty - sl.qty_received
                    new_val["date_expected"] = sl.date_planned
                    product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(
                        remaining_qty, quant_uom
                    )
                    new_val["product_uom_qty"] = product_uom_qty
                    new_val["product_uom"] = product_uom.id
                    new_vals.append(new_val)
            else:
                new_vals.append(val)
        return new_vals
