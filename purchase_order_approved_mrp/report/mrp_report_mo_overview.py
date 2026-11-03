# Copyright 2026 Versada UAB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ReportMoOverview(models.AbstractModel):
    _inherit = "report.mrp.report_mo_overview"

    def _get_extra_replenishments(self, product):
        """Count approved orders like RFQs: they have no receipt yet."""
        res = super()._get_extra_replenishments(product)
        domain = [("state", "=", "approved"), ("product_id", "=", product.id)]
        warehouse_id = self.env["stock.warehouse"]._get_warehouse_id_from_context()
        if warehouse_id:
            domain += [("order_id.picking_type_id.warehouse_id", "=", warehouse_id)]
        po_lines = self.env["purchase.order.line"].search(
            domain, order="date_planned, id"
        )
        for po_line in po_lines:
            line_qty = po_line.product_qty
            dest_moves = self.env["stock.move"].browse(
                po_line.move_dest_ids._rollup_move_dests()
            )
            for move in dest_moves:
                if not move.raw_material_production_id:
                    continue
                production_qty = min(
                    line_qty,
                    move.product_uom._compute_quantity(
                        move.product_uom_qty, po_line.product_uom
                    ),
                )
                res.append(
                    self._format_extra_replenishment(
                        po_line, production_qty, move.raw_material_production_id.id
                    )
                )
                line_qty -= production_qty
            if line_qty:
                res.append(self._format_extra_replenishment(po_line, line_qty))
        return res
