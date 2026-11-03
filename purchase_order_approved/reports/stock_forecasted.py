# Copyright 2026 Versada UAB
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockForecasted(models.AbstractModel):
    _inherit = "stock.forecasted_product_product"

    def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
        """Count approved orders like RFQs: they have no receipt yet."""
        res = super()._get_report_header(
            product_template_ids, product_ids, wh_location_ids
        )
        domain = [("state", "=", "approved")]
        domain += self._product_purchase_domain(product_template_ids, product_ids)
        warehouse_id = self.env["stock.warehouse"]._get_warehouse_id_from_context()
        if warehouse_id:
            domain += [("order_id.picking_type_id.warehouse_id", "=", warehouse_id)]
        po_lines = self.env["purchase.order.line"].search(domain)
        if not po_lines:
            return res
        in_sum = sum(po_lines.mapped("product_uom_qty"))
        draft_order_ids = [order["id"] for order in res["draft_purchase_orders"]]
        orders = self.env["purchase.order"].browse(draft_order_ids) | po_lines.mapped(
            "order_id"
        )
        line_to_match_id = self.env.context.get("purchase_line_to_match_id")
        res.update(
            draft_purchase_qty=res["draft_purchase_qty"] + in_sum,
            draft_purchase_orders=orders.sorted(key=lambda order: order.name).read(
                fields=["id", "name"]
            ),
            draft_purchase_orders_matched=res["draft_purchase_orders_matched"]
            or line_to_match_id in po_lines.ids,
        )
        res["qty"]["in"] += in_sum
        return res
