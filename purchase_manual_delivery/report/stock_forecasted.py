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
        warehouse_id = self.env.context.get("warehouse_id", False)
        if warehouse_id:
            domain += [("order_id.picking_type_id.warehouse_id", "=", warehouse_id)]
        po_lines = (
            self.env["purchase.order.line"].sudo().search(domain).grouped("product_id")
        )
        in_qty = {
            product.id: sum(
                lines.mapped(
                    lambda pol: pol.product_qty
                    - (pol.qty_in_receipt + pol.qty_received)
                )
            )
            for product, lines in po_lines.items()
        }
        self._add_product_quantities(
            res, product_template_ids, product_ids, "no_delivery_purchase_qty", in_qty
        )
        for product in self._get_products(product_template_ids, product_ids):
            if product not in po_lines:
                continue
            res["product"][product.id]["no_delivery_purchase_orders"] = (
                po_lines[product]
                .mapped("order_id")
                .sorted("name")
                .read(fields=["id", "name"])
            )
        return res
