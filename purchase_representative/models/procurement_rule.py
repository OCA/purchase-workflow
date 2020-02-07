# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    @api.multi
    def _run_buy(
            self, product_id, product_qty, product_uom,
            location_id, name, origin, values
    ):
        values["propagate_create_uid"] = self.env.uid
        return super()._run_buy(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)

    def _prepare_purchase_order(self, product_id, product_qty, product_uom,
                                origin, values, partner):
        vals = super()._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, partner)
        if values.get("propagate_create_uid"):
            vals.update({
                "user_id": values.get("propagate_create_uid"),
            })
        return vals
