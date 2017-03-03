# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.multi
    def _is_subcontracted_service(self):
        self.ensure_one()
        return (self.product_id.type == 'service' and
                self.product_id.property_subcontracted_service or
                False)

    @api.model
    def _find_suitable_rule(self, procurement):
        res = super(ProcurementOrder, self)._find_suitable_rule(procurement)
        if procurement._is_subcontracted_service():
            return (
                procurement.warehouse_id.subcontracting_service_proc_rule_id.id
            )
        return res

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if not res:
            rule_id = self._find_suitable_rule(procurement)
            if rule_id:
                procurement.write({'rule_id': rule_id})
                return True
        return res
