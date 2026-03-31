# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _pre_action_done_hook(self):
        # Skip backorder wizard creation based on purchase order line threshold.
        #
        # If any move's quantity falls within the threshold specified in the PO line,
        # it sets the context key `skip_backorder` to skip backorder wizard creation.
        skip_backorder = any(
            self.filtered(lambda p: p.purchase_id).mapped(
                lambda p: any(
                    move.purchase_line_id._check_threshold(move.quantity)
                    for move in p.move_ids
                )
            )
        )
        if skip_backorder:
            self = self.with_context(skip_backorder=True)
        return super()._pre_action_done_hook()

    def _action_done(self):
        # Prevent creating backorders based on purchase order line threshold.
        #
        # If any move's quantity falls within the threshold specified in PO line,
        # it sets the context key `cancel_backorder (backorders won't be created).
        cancel_backorder = any(
            self.filtered(lambda p: p.purchase_id).mapped(
                lambda p: any(
                    move.purchase_line_id._check_threshold(move.quantity)
                    for move in p.move_ids
                )
            )
        )
        if cancel_backorder:
            self = self.with_context(cancel_backorder=True)
        return super()._action_done()
