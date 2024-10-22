# Copyright 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_order_weight_in_po = fields.Boolean(
        related="company_id.display_order_weight_in_po",
        readonly=False,
    )
    display_order_volume_in_po = fields.Boolean(
        related="company_id.display_order_volume_in_po",
        readonly=False,
    )
