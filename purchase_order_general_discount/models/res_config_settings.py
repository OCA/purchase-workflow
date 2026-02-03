# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_general_discount_field = fields.Selection(
        related="company_id.purchase_general_discount_field",
        readonly=False,
    )
