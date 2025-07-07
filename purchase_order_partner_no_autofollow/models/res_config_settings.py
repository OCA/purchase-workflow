from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_partner_disable_autofollow = fields.Boolean(
        config_parameter="purchase_order_partner_no_autofollow.partner_disable_autofollow",
        string="Customer disable autofollow",
    )
