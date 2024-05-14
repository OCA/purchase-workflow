# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sending_error_type = fields.Selection(
        selection=[("email_not_sent", "Email not sent")]
    )

    transmission_error = fields.Boolean(
        store=True,
        compute="_compute_transmission_error",
        string="Error in sending",
    )

    @api.depends("sending_error_type")
    def _compute_transmission_error(self):
        for rec in self:
            rec.transmission_error = rec.sending_error_type == "email_not_sent"
