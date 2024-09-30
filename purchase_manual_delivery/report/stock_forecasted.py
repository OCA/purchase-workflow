from odoo import models


class ReplenishmentReport(models.AbstractModel):
    _inherit = "report.stock.report_product_product_replenishment"

    def _serialize_docs(
        self, docs, product_template_ids=False, product_variant_ids=False
    ):
        res = super()._serialize_docs(docs, product_template_ids, product_variant_ids)
        res["no_delivery_purchase_orders"] = docs["no_delivery_purchase_orders"].read(
            fields=["id", "name"]
        )
        return res

    def _compute_draft_quantity_count(
        self, product_template_ids, product_variant_ids, wh_location_ids
    ):
        res = super()._compute_draft_quantity_count(
            product_template_ids, product_variant_ids, wh_location_ids
        )
        domain = [
            ("state", "in", ["purchase", "done"]),
            ("pending_to_receive", "=", True),
        ]
        domain += self._product_domain(product_template_ids, product_variant_ids)
        warehouse_id = self.env.context.get("warehouse", False)
        if warehouse_id:
            domain += [("order_id.picking_type_id.warehouse_id", "=", warehouse_id)]
        po_lines = self.env["purchase.order.line"].search(domain)
        in_sum = sum(po_lines.mapped(lambda po: po.product_qty - po.existing_qty))
        res["no_delivery_purchase_qty"] = in_sum
        res["no_delivery_purchase_orders"] = po_lines.mapped("order_id").sorted("name")
        res["qty"]["in"] += in_sum
        return res
