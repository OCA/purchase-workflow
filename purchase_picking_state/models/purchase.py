# Copyright 2016 Chafique DELLI @ Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools.translate import _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_picking_state(self):
        return [
            ("draft", ""),
            ("cancel", _("Cancelled")),
            ("not_received", _("Not Received")),
            ("partially_received", _("Partially Received")),
            ("done", _("Transferred")),
        ]

    @api.depends("picking_ids", "picking_ids.state")
    def _compute_picking_state(self):
        for purchase in self:
            if purchase.picking_ids:
                pickings_state = {picking.state for picking in purchase.picking_ids}
                if pickings_state == {"cancel"}:
                    purchase.picking_state = "cancel"
                elif pickings_state == {"cancel", "done"} or pickings_state == {"done"}:
                    purchase.picking_state = "done"
                elif "done" in pickings_state:
                    purchase.picking_state = "partially_received"
                else:
                    purchase.picking_state = "not_received"
            else:
                purchase.picking_state = "draft"

    picking_state = fields.Selection(
        string="Picking status",
        readonly=True,
        compute="_compute_picking_state",
        store=True,
        selection="get_picking_state",
        help="Overall status based on all pickings",
    )
