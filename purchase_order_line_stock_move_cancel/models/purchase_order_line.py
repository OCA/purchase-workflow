# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.fields import Command


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    can_cancel_moves = fields.Boolean(
        compute="_compute_can_cancel_moves",
        help="This is a technical fields in order to display the cancel button",
    )

    def _compute_can_cancel_moves(self):
        """
        All moves from a purchase order line should not be cancelled or done
        """
        for line in self:
            line.can_cancel_moves = bool(
                line.move_ids
                and all(move.state not in ("done", "cancel") for move in line.move_ids)
            )

    def _log_cancel_moves(self):
        """
        Log lines that have been cancelled in purchase order
        """
        for purchase, lines in self.partition("order_id").items():
            body = _("Lines that have been cancelled:<br/>")
            body += "<ul>"
            body += "<li>".join([line.display_name + "</li>" for line in lines])
            body += "</ul>"
            purchase.message_post(body=body)

    def _cancel_moves(self) -> bool:
        """
        Allows to cancel stock moves from purchase order lines

        :return: _description_
        :rtype: bool
        """
        moves_to_cancel = self.move_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        for move in moves_to_cancel:
            move._action_cancel()
        moves_to_cancel.purchase_line_id._log_cancel_moves()
        return True

    def action_cancel_moves(self):
        self.ensure_one()
        wizard = self.env["purchase.order.line.stock.move.cancel"].create(
            {"purchase_line_ids": [Command.set(self.ids)]}
        )
        view = self.env.ref(
            "purchase_order_line_stock_move_cancel.purchase_order_line_stock_move_cancel_form"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Cancel Stock Moves"),
            "view_mode": "form",
            "res_model": "purchase.order.line.stock.move.cancel",
            "target": "new",
            "res_id": wizard.id,
            "views": [[view.id, "form"]],
        }
