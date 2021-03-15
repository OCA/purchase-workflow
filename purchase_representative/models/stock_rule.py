# Copyright 2020-21 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_buy(self, procurements):
        for procurement, _rule in procurements:
            procurement.values["propagate_create_uid"] = self.env.uid
        return super()._run_buy(procurements)

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        create_uids = [v.get("propagate_create_uid") for v in values]
        create_uids = list(set(create_uids))
        if len(create_uids) == 1:
            vals.update({"user_id": create_uids[0]})
        return vals
