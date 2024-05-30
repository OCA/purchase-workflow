# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_cancel_remaining_delivery(self):
        for purchase in self:
            if purchase.state not in ("purchase", "done"):
                continue
            picking_to_cancel = purchase.picking_ids.filtered(
                lambda pick: pick.state in ("assigned", "waiting", "confirmed")
            )
            picking_to_cancel.action_cancel()
