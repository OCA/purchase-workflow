from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_use_only_supplied_product = fields.Boolean(
        string='Enable "Use only allowed products" by default',
        default_model="purchase.order",
    )
