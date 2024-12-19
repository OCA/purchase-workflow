# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    active = fields.Boolean(default=True)

    def toggle_active(self):
        if self.filtered(lambda po: po.state not in ["done", "cancel"] and po.active):
            raise UserError(_("Only 'Locked' or 'Canceled' orders can be archived"))
        return super().toggle_active()

    @api.constrains("state")
    def _check_state(self):
        for rec in self:
            if not rec.active:
                raise UserError(
                    _(
                        "This record is currently archived and cannot have its state "
                        "modified. Please unarchive the record to make changes. "
                    )
                )
