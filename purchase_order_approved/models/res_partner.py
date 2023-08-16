# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    purchase_requires_second_approval = fields.Selection(
        selection=[
            ("never", "Never"),
            ("based_on_company", "Based on company policy"),
            ("always", "Always"),
        ],
        default="based_on_company",
        copy=False,
    )
