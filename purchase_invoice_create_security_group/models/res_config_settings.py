# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    purchase_invoice_create_security = fields.Boolean(
        related="company_id.purchase_invoice_create_security", readonly=False
    )
