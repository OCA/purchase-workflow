# Copyright 2025 Juan Alberto Raja<juan.raja@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    purchase_pricelist_disable_autocreate = fields.Boolean(
        related="company_id.purchase_pricelist_disable_autocreate",
        string="Enable Automatic Supplier Pricelists",
        readonly=False,
        help=(
            "When enabled, the system will automatically create supplier "
            "pricelists when validating purchase orders."
        ),
    )
