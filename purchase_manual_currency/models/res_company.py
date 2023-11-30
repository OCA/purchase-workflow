# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    manual_currency_po_inv = fields.Selection(
        selection=[
            ("currency_inv", "Use currency invoice"),
            ("currency_po", "Use currency purchase"),
        ],
        default="currency_inv",
        string="Manual Currency Purchase - Invoice",
    )
