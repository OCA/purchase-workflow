# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _skip_procurement(self, procurement):
        res = super()._skip_procurement(procurement)
        if self._is_subcontracted_service_procurement(procurement.product_id):
            return False
        return res

    @api.model
    def _has_subcontracted_service_procurement(self, product_id):
        return product_id.type == "product" and product_id.subcontracted_product_id

    @api.model
    def _is_subcontracted_service_procurement(self, product_id):
        return (
            product_id.type == "service"
            and self.env["product.template"].search_count(
                [("subcontracted_product_id", "=", product_id.id)]
            )
            > 0
        )

    @api.model
    def _get_rule(self, product_id, location_id, values):
        res = super()._get_rule(product_id, location_id, values)
        if self._has_subcontracted_service_procurement(product_id):
            self.trigger_service_procurement(product_id, location_id, values)
        return res

    def trigger_service_procurement(self, product_id, location_id, values):
        errors = []
        procurements = []
        try:
            procurement = self.Procurement(
                product_id.subcontracted_product_id,
                1.0,
                product_id.subcontracted_product_id.uom_id,
                location_id,
                values.get("origin") or "Procure service for %s" % product_id.name,
                values.get("origin") or "Procure service for %s" % product_id.name,
                self.env.company,
                values,
            )

            procurements.append(procurement)
            # Trigger a route check with a mutable in the context that can be
            # cleared after the first rule selection
            self.env["procurement.group"].run(procurements)
        except UserError as error:
            errors.append(error.args[0])
        if errors:
            raise UserError("\n".join(errors))
        return procurements
