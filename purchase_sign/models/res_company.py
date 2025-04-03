# Copyright 2025 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_portal_confirmation_sign = fields.Boolean(
        string="Online Signature",
        default=False,
        help="Enable this to request a digital signature when confirming "
        "Purchase Orders via the portal.",
    )
