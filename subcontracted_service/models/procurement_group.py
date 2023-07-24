# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# Copyright 2017-23 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _skip_procurement(self, procurement):
        res = super()._skip_procurement(procurement)
        if self._is_subcontracted_service(procurement.product_id):
            return False
        return res

    @api.model
    def _is_subcontracted_service(self, product_id):
        return (
            product_id.type == "service" and product_id.property_subcontracted_service
        )

    @api.model
    def _get_rule(self, product_id, location_id, values):
        res = super()._get_rule(product_id, location_id, values)
        if self._is_subcontracted_service(product_id):
            warehouse = values.get("warehouse_id") or location_id.get_warehouse()
            rule_id = warehouse.subcontracting_service_proc_rule_id
            if rule_id:
                return rule_id
        return res
