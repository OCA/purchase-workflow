# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _is_subcontracted_service(self, procurement):
        return (procurement.product_id.type == 'service' and
                procurement.product_id.property_subcontracted_service or
                False)

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if not res:
            return self._is_subcontracted_service(procurement)
        return res

    @api.model
    def _run(self, procurement):
        if self._is_subcontracted_service(procurement):
            return self._create_po_subcontracted(procurement)
        return super(ProcurementOrder, self)._run(procurement)

    @api.multi
    def find_subcontracting_rule(self):
        self.ensure_one()
        rule = self.company_id.subcontracting_service_proc_rule_id
        return rule

    @api.model
    def _create_po_subcontracted(self, procurement):
        rule = procurement.find_subcontracting_rule()
        if rule:
            procurement.rule_id = rule
            res = procurement.make_po()
            return res
        else:
            procurement.message_post(body=_(
                'No subscription rule associated to company %s. '
                'Please set one to fix this procurement.') % (
                procurement.company_id.name))
            return procurement.id


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    is_subcontracting_rule = fields.Boolean(default=False)
