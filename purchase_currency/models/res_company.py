# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_purchase_currency_id = fields.Many2one(
        comodel_name="res.currency", string="Default Purchase Currency"
    )
