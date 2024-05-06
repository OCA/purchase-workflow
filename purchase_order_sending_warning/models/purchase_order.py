# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sending_warning = fields.Selection(selection=[("email_not_sent", "Email not sent")])

    error_in_sending = fields.Boolean(
        store=True,
        compute="_compute_error_in_sending",
        string="Error in sending",
    )

    @api.depends("sending_warning")
    def _compute_error_in_sending(self):
        for rec in self:
            rec.error_in_sending = rec.sending_warning == "email_not_sent"
