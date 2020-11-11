# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockRule(models.Model):

    _inherit = "stock.rule"

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """Add procurement group to values"""
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        procurement_group = values.get("group_id")
        if procurement_group:
            res["procurement_group_id"] = procurement_group.id
        return res
