from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_use_only_supplied_product = fields.Boolean(
        related="company_id.force_only_supplied_product",
        default_model="purchase.order",
        readonly=False,
    )
