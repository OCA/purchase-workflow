# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.multi
    def _is_subcontracted_service(self):
        self.ensure_one()
        return (self.product_id.type == 'service' and
                self.product_id.property_subcontracted_service or
                False)

    @api.multi
    def _find_suitable_rule(self):
        res = super(ProcurementOrder, self)._find_suitable_rule()
        if self._is_subcontracted_service():
            return (
                self.warehouse_id.subcontracting_service_proc_rule_id
            )
        return res

    @api.multi
    def _assign(self):
        res = super(ProcurementOrder, self)._assign()
        if not res:
            rule_id = self._find_suitable_rule()
            if rule_id:
                self.write({'rule_id': rule_id.id})
                return True
        return res
