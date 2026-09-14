# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
        po,
    ):
        # For new PO lines we set the product packaging if present in
        # the procurement values.
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
            po,
        )
        packaging_uom = values.get("packaging_uom_id")
        if packaging_uom:
            res["product_uom_id"] = packaging_uom.id
            res["product_qty"] = product_uom._compute_quantity(
                product_qty, packaging_uom
            )
        return res
