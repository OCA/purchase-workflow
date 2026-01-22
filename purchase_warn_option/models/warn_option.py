# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class WarnOption(models.Model):
    _inherit = "warn.option"

    allowed_warning_usage = fields.Selection(
        selection_add=[
            ("partner_purchase_warn", "(Partner) Warning on the Purchase Order"),
            ("product_purchase_warn", "(Product) Warning when Purchasing this Product"),
        ],
        ondelete={
            "partner_purchase_warn": "set default",
            "product_purchase_warn": "set default",
        },
    )
