# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        """
        Add purchase tags coming from route to existing purchase line
        """
        res = super()._update_purchase_order_line(
            product_id=product_id,
            product_qty=product_qty,
            product_uom=product_uom,
            company_id=company_id,
            values=values,
            line=line,
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
