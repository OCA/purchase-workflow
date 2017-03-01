# -*- coding: utf-8 -*-
# Copyright 2015 Avanzosc(http://www.avanzosc.es)
# Copyright 2015 Tecnativa (http://www.tecnativa.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        if procurement.product_id.type == 'service':
            rule_id = self._find_suitable_rule(procurement)
            if rule_id:
                procurement.rule_id = rule_id
            res = bool(rule_id)
        return res
