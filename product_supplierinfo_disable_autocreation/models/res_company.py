# Copyright 2025 Juan Alberto Raja<juan.raja@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    purchase_pricelist_disable_autocreate = fields.Boolean(
        string="Enable Automatic Supplier Pricelists",
        help=(
            "When enabled, the system will automatically create supplier "
            "pricelists when validating purchase orders."
        ),
        default=True,
    )
