# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    purchase_request_ids = fields.Many2many(
        comodel_name="purchase.request",
        string="Purchase Requests",
    )
    model = fields.Selection(
        selection_add=[
            ("purchase.request", "Purchase request"),
            ("purchase.request.line", "Purchase request line"),
        ],
        ondelete={"purchase.request": "cascade", "purchase.request.line": "cascade"},
    )
