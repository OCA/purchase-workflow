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
                "order_id",
                "product_uom",
                "orderpoint_id",
            ],
            ["product_qty:sum", "qty_in_receipt:sum", "qty_received:sum"],
        )
        for (
            product,
            order,
            uom,
            orderpoint,
            product_qty,
            qty_in_receipt,
            qty_received,
        ) in groups:
            if orderpoint:
                location = orderpoint.location_id
            else:
                location = order.picking_type_id.default_location_dest_id
            product_qty = uom._compute_quantity(
                product_qty, product.uom_id, round=False
            )
            remaining_qty = product_qty - (qty_in_receipt + qty_received)
            qty_by_product_location[(product.id, location.id)] += remaining_qty
            qty_by_product_wh[(product.id, location.warehouse_id.id)] += remaining_qty
        return qty_by_product_location, qty_by_product_wh
