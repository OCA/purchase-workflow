# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_portal_confirmation_sign = fields.Boolean(
        string="Purchase Online Signature", default=False
    )
