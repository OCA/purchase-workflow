# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    group_id = fields.Many2one(comodel_name="procurement.group", string="Group")

    def _prepare_tender_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        res = super()._prepare_tender_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        res["group_id"] = values.get("group_id").id or False
        return res

    @api.model
    def create(self, vals):
        """It is not possible to intercept _run_buy() to add lines instead of creating
        multiple records.
        This method is used to find if there is any previously created record with
        the same values to add the line instead of creating a new record.
        """
        if self.env.context.get("grouped_by_procurement") and vals.get("group_id"):
            domain = []
            for key in vals:
                if key == "line_ids":
                    continue
                domain.append((key, "=", vals.get(key)))
            purchase = self.search(domain)
            if purchase:
                purchase.write({"line_ids": vals.get("line_ids")})
                return purchase
        return super().create(vals)
