# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        values = super()._prepare_procurement_values()
        # At this time, we assert the move that launch the buy
        # rule is triggered by a move created by the
        # tagged rule.
        # TODO: check if storing the tags on the move is
        # necessary or not.
        if self.rule_id.route_id.purchase_tag_ids:
            if "purchase_tag_ids" in values:
                values["purchase_tag_ids"] |= self.rule_id.route_id.purchase_tag_ids
            else:
                values["purchase_tag_ids"] = self.rule_id.route_id.purchase_tag_ids
        return values
