# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    branch_id = fields.Many2one(
        comodel_name="res.branch",
    )
