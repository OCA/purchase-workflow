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
            groups = rec.mapped("picking_ids.group_id")
            all_picking_ids = self.env["stock.picking"].search(
                [("group_id", "in", groups.ids)]
            )
            rec.all_picking_ids = all_picking_ids

    def action_view_all_pickings(self):
        """Similar to the view_picking method in the purchase module"""
        action_data = self.env.ref("stock.action_picking_tree_all").read()[0]
        pickings = self.mapped("all_picking_ids")

        # override the context to get rid of the default filtering on
        # picking type
        action_data["context"] = {}

        # choose the view_mode accordingly
        if len(pickings) > 1:
            action_data["domain"] = [("id", "in", pickings.ids)]
        else:
            form_view = self.env.ref("stock.view_picking_form")
            action_data["views"] = [(form_view.id, "form")]
            action_data["res_id"] = pickings.id
        return action_data
