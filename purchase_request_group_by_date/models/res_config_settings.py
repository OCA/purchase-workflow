from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_group_purchase_request = fields.Boolean(
        related="company_id.group_purchase_request", readonly=False
    )
