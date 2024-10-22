# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    receipt_threshold = fields.Float(
        default=0.0,
        required=True,
        groups="purchase.group_purchase_manager",
    )
