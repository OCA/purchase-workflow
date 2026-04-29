# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_purchase_force_vendor_restrict = fields.Boolean(
        string="Restrict allowed vendors in sale orders",
        related="company_id.sale_purchase_force_vendor_restrict",
        readonly=False,
    )
