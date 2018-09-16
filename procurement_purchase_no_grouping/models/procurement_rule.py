# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id,
                 name, origin, values):
        grouping = product_id.categ_id.procured_purchase_grouping
        self_wc = self.with_context(grouping=grouping)
        return super(ProcurementRule, self_wc)._run_buy(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)

    def _make_po_get_domain(self, values, partner):
        if self.env.context.get('grouping', 'standard') == 'order':
            return (('id', '=', 0), )
        return super()._make_po_get_domain(values, partner)
