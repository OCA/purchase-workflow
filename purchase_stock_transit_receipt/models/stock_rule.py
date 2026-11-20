# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        purchase_values = super()._prepare_purchase_order(company_id, origins, values)
        purchase_values["picking_type_id"] = (
            self.env["purchase.order"]
            .with_company(company_id)
            .new(purchase_values)
            ._get_receipt_picking_type(self.picking_type_id)
            .id
        )
        return purchase_values

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        transit_type = self.picking_type_id.warehouse_id.transit_in_type_id
        if not transit_type:
            return domain
        picking_type_leaf = ("picking_type_id", "=", self.picking_type_id.id)
        return tuple(
            ("picking_type_id", "in", tuple((self.picking_type_id | transit_type).ids))
            if leaf == picking_type_leaf
            else leaf
            for leaf in domain
        )

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        values = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        move_dests = move_to_copy._get_open_transit_move_dests()
        if move_dests:
            values["move_dest_ids"] = [Command.set(move_dests.ids)]
        return values
