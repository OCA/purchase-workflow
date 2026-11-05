# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCOmpany(models.Model):
    _inherit = "res.company"

    purchase_update_date_planned_at_confirm = fields.Boolean(
        help="Check this if you want to update the planned date "
    )
