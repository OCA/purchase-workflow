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
