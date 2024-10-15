# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_order_confirm_partial_enabled = fields.Boolean(
        string="Partial Confirmation",
        config_parameter="purchase_order_confirm_partial.enabled",
    )
    po_confirm_partial_save_unconfirmed = fields.Boolean(
        string="Save Unconfirmed Items",
        config_parameter="purchase_order_confirm_partial.save_unconfirmed",
        help=(
            "If enabled a new RFQ in the 'Cancel' "
            "state will be created with all the lines "
            "that were not confirmed."
        ),
    )
    po_confirm_partial_unconfirmed_suffix = fields.Char(
        string="Unconfirmed RFQ Suffix",
        config_parameter="purchase_order_confirm_partial.unconfirmed_suffix",
        default="-U",
    )
