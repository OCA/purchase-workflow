# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, api, models


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
        """
        Add purchase tags coming from route to new purchase line
        """
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
        if "route_ids" in values:
            tag_ids = values.get("route_ids").purchase_tag_ids
            if tag_ids:
                if res.get("tag_ids"):
                    res["tag_ids"].update(
                        [Command.link(tag_id.id) for tag_id in tag_ids]
                    )
                else:
                    res["tag_ids"] = [Command.link(tag_id.id) for tag_id in tag_ids]
        return res
