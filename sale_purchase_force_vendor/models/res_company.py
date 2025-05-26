# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_purchase_force_vendor_restrict = fields.Boolean(
        string="Restrict allowed vendors in sale orders",
        default=True,
    )
