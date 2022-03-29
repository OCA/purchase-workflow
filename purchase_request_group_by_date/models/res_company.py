# Copyright 2022 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    group_purchase_request = fields.Boolean(
        string="Group purchase request by product and date",
        help="Updates data on existing purchase request for product \
        and date instead of creating new request.",
    )
