from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_pending_lines_domain(self, location_ids=False, warehouse_ids=False):
        domain = self._get_lines_domain(location_ids, warehouse_ids)
        for domain_part in domain:
            if (
                isinstance(domain_part, tuple)
                and len(domain_part) == 3
                and domain_part[0] == "state"
            ):
                domain_index = domain.index(domain_part)
                domain[domain_index] = ("state", "in", ("purchase", "done"))
                domain.insert(domain_index + 1, ("pending_to_receive", "=", True))
                domain.insert(domain_index, "&")
                break
        return domain

    def _get_quantity_in_progress(self, location_ids=False, warehouse_ids=False):
        qty_by_product_location, qty_by_product_wh = super()._get_quantity_in_progress(
            location_ids, warehouse_ids
        )
        domain = self._get_pending_lines_domain(location_ids, warehouse_ids)
        groups = self.env["purchase.order.line"]._read_group(
            domain,
            [
                "product_id",
                "product_qty",
                "order_id",
                "product_uom",
                "orderpoint_id",
                "existing_qty",
            ],
            ["order_id", "product_id", "product_uom", "orderpoint_id"],
            lazy=False,
        )
        for group in groups:
            if group.get("orderpoint_id"):
                location = (
                    self.env["stock.warehouse.orderpoint"]
                    .browse(group["orderpoint_id"][:1])
                    .location_id
                )
            else:
                order = self.env["purchase.order"].browse(group["order_id"][0])
                location = order.picking_type_id.default_location_dest_id
            product = self.env["product.product"].browse(group["product_id"][0])
            uom = self.env["uom.uom"].browse(group["product_uom"][0])
            product_qty = uom._compute_quantity(
                group["product_qty"], product.uom_id, round=False
            )
            remaining_qty = product_qty - group["existing_qty"]
            qty_by_product_location[(product.id, location.id)] += remaining_qty
            qty_by_product_wh[(product.id, location.warehouse_id.id)] += remaining_qty
        return qty_by_product_location, qty_by_product_wh
