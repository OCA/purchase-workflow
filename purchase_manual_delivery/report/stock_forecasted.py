from odoo import models


class StockForecastedProductProduct(models.AbstractModel):
    _inherit = "stock.forecasted_product_product"

    def _get_report_header(self, product_template_ids, product_ids, wh_location_ids):
        """Insert entries for POs for which additional receipts can be created"""
        res = super()._get_report_header(
            product_template_ids, product_ids, wh_location_ids
        )
        domain = [
            ("state", "in", ["purchase", "done"]),
            ("pending_to_receive", "=", True),
        ]
        domain += self._product_purchase_domain(product_template_ids, product_ids)
        warehouse_id = self.env.context.get("warehouse", False)
        if warehouse_id:
            domain += [("order_id.picking_type_id.warehouse_id", "=", warehouse_id)]
        po_lines = self.env["purchase.order.line"].search(domain)
        in_sum = sum(
            po_lines.mapped(
                lambda pol: pol.product_qty - (pol.qty_in_receipt + pol.qty_received)
            )
        )
        res["no_delivery_purchase_qty"] = in_sum
        res["no_delivery_purchase_orders"] = (
            po_lines.mapped("order_id").sorted("name").read(fields=["id", "name"])
        )
        res["qty"]["in"] += in_sum
        return res
