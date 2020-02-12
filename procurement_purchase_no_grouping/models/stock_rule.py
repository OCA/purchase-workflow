# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_buy(self, procurements):
        for procurement, _rule in procurements:
            procurement.values[
                "grouping"
            ] = procurement.product_id.categ_id.procured_purchase_grouping
        return super()._run_buy(procurements)

    def _make_po_get_domain(self, company_id, values, partner):
        if values.get("grouping") == "order":
            return (("id", "=", 0),)
        return super()._make_po_get_domain(company_id, values, partner)
