# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        move_dest_recs = values.get("move_dest_ids")
        if move_dest_recs:
            origin_move = move_dest_recs[0]
            if origin_move.restrict_partner_id:
                domain += (("owner_id", "=", origin_move.restrict_partner_id.id),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super(StockRule, self)._prepare_purchase_order(
            company_id, origins, values
        )
        values = values[0]
        move_dest = values.get("move_dest_ids")
        if move_dest:
            # TODO: Should we simply get restrict_partner_id from move_dest?
            if move_dest.picking_id.owner_id:
                vals["owner_id"] = move_dest.picking_id.owner_id.id
            else:
                # Handle the case where mrp_production_ids exists
                mrp_productions = getattr(
                    move_dest.group_id, "mrp_production_ids", None
                )
                if mrp_productions:
                    vals["owner_id"] = mrp_productions[0].owner_id.id
        return vals
