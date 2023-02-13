from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_product_image_in_purchase_report = fields.Boolean(
        "Show Product Image In Purchase Report",
        config_parameter="purchase_order_line_image.show_product_image_in_purchase_report",
    )
