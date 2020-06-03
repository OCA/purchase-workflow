# Copyright 2020 Camptocamp SA
# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        # For new PO lines we set the product packaging if present in
        # the procurement values.
        vals = super()._prepare_purchase_order_line(
            product_id=product_id,
            product_qty=product_qty,
            product_uom=product_uom,
            company_id=company_id,
            values=values,
            po=po,
        )
        if values.get("product_packaging_id"):
            vals["product_packaging"] = values.get("product_packaging_id").id
        return vals
