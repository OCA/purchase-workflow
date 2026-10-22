# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    all_picking_ids = fields.One2many(
        "stock.picking", string="All Pickings", compute="_compute_all_pickings"
    )
    all_picking_count = fields.Integer(
        "All Pickings Count", compute="_compute_all_picking_count"
    )

    def _compute_all_picking_count(self):
        for rec in self:
            rec.all_picking_count = len(rec.all_picking_ids)

    def _compute_all_pickings(self):
        for rec in self:
            moves = rec.order_line.move_ids
            rec.all_picking_ids = (
                rec.picking_ids | moves._get_reception_chain_moves().picking_id
            )

    def action_view_all_pickings(self):
        return self._get_action_view_all_pickings(self.all_picking_ids)

    def _get_action_view_all_pickings(self, picking_ids):
        """Same action as the core receipts button, for all the given pickings"""
        result = self._get_action_view_picking(picking_ids)
        # override the context to get rid of the receipt defaults
        result["context"] = {}
        return result
