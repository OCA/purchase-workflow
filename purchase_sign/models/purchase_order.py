# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    require_signature = fields.Boolean(
        string="Online Signature",
        compute="_compute_require_signature",
        store=True,
        readonly=False,
        precompute=True,
        help="Request an online signature from the supplier "
        "to confirm orders automatically.",
    )

    signature = fields.Image(
        copy=False, attachment=True, max_width=1024, max_height=1024
    )

    signed_by = fields.Char(copy=False)
    signed_on = fields.Datetime(copy=False)

    @api.depends("company_id")
    def _compute_require_signature(self):
        for order in self:
            order.require_signature = bool(
                order.company_id.purchase_portal_confirmation_sign
            )

    def _has_to_be_signed(self):
        """Checks whether this purchase order requires signature."""
        self.ensure_one()
        return self.state == "sent" and self.require_signature and not self.signature
