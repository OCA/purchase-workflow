# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_restricted = fields.Boolean(
        "Restrict Access",
        tracking=True,
        help="If selected, this purchase order can only be accessed by the assigned "
        "buyer or purchase managers.",
    )

    @api.constrains("is_restricted")
    def _check_is_restricted_access(self):
        for order in self:
            if order.user_id != self.env.user and not self.user_has_groups(
                "purchase.group_purchase_manager"
            ):
                raise ValidationError(
                    _("You do not have the right to change Restrict Access setting.")
                )
