# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_id = fields.Many2one(
        comodel_name="purchase.order.cancel.reason",
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict",
    )

    def action_open_cancel_wizard(self):
        """
        Open the cancellation wizard with the selected purchase orders.
        Raise a warning if all orders are in the 'done' or 'cancel' state.
        Otherwise, proceed with the wizard for valid orders.
        """
        restricted_states = ["done", "cancel"]
        invalid_orders, valid_orders = (
            self.filtered(lambda po: po.state in restricted_states),
            self.filtered(lambda po: po.state not in restricted_states),
        )
        if not valid_orders:
            raise ValidationError(
                _(
                    "You cannot cancel any of the selected orders as "
                    "they are all in 'Done' or 'Canceled' state:\n%s"
                )
                % "\n".join(invalid_orders.mapped("name"))
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Reason for Cancellation"),
            "res_model": "purchase.order.cancel",
            "view_mode": "form",
            "target": "new",
            "context": {"default_purchase_order_ids": valid_orders.ids},
        }
