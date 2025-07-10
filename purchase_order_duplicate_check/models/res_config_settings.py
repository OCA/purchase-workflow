from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_create_activity_repeating_orders = fields.Boolean(
        config_parameter="purchase_order_duplicate_check.allow_create_activity_repeating_orders"
    )
    repeating_orders_activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        config_parameter="purchase_order_duplicate_check.repeating_orders_activity_type_id",
        string="Activity",
    )

    @api.onchange("allow_create_activity_repeating_orders")
    def _onchange_allow_create_activity_repeating_orders(self):
        if not self.allow_create_activity_repeating_orders:
            self.repeating_orders_activity_type_id = False
