# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_packaging_default_enabled = fields.Boolean(
        help="In purchase order line get 1st packaging found in product configuration",
    )
