# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2020 Radovan Skolnik
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_buy(self, procurements):
        for procurement, _rule in procurements:
            grouping = procurement.product_id.categ_id.procured_purchase_grouping
            if not grouping:
                grouping = self.env.company.procured_purchase_grouping
            procurement.values["grouping"] = grouping
        return super()._run_buy(procurements)

    def _make_po_get_domain(self, company_id, values, partner):
        """Inject an impossible domain for not getting match in case of no order
        grouping.

        We try to make it the more unique possible for avoiding coincidences for not
        overlapping in a batch procurement run (like a sales order with multiple MTO
        lines confirmation).
        """
        domain = super()._make_po_get_domain(company_id, values, partner)
        if values.get("grouping") == "order":
            if values.get("move_dest_ids"):
                domain += (("id", "=", -values["move_dest_ids"][:1].id),)
            # The minimum is imposed by PG int4 limit
            domain += (("id", "=", random.randint(-2147483648, 0)),)
        return domain
