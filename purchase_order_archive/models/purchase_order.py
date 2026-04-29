# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    active = fields.Boolean(default=True)

    def action_archive(self):
        if self.filtered(lambda po: po.state != "cancel" and not po.locked):
            raise UserError(
                self.env._("Only 'Locked' or 'Canceled' orders can be archived")
            )
        return super().action_archive()

    @api.constrains("state", "locked")
    def _check_state(self):
        for rec in self:
            if not rec.active:
                raise UserError(
                    self.env._(
                        "This record is currently archived and cannot have its state "
                        "modified. Please unarchive the record to make changes. "
                    )
                )
