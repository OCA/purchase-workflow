# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.model
    def create(self, vals):
        """It is not possible to intercept _run_buy() to add lines instead of creating
        multiple records.
        This method is used to find if there is any previously created record with
        the same values to add the line instead of creating a new record.
        """
        if self.env.context.get("grouped_by_procurement") and vals.get(
            "procurement_group_id"
        ):
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
