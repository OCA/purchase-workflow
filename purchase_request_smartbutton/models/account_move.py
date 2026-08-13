# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_request_ids = fields.Many2many(
        comodel_name="purchase.request",
        string="Purchase Requests",
        compute="_compute_purchase_request_ids",
        help="Requests behind the purchase orders this bill came from.",
    )
    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_ids",
    )

    @api.depends("invoice_line_ids.purchase_line_id.purchase_request_lines.request_id")
    def _compute_purchase_request_ids(self):
        for move in self:
            request_lines = move.invoice_line_ids.purchase_line_id
            requests = request_lines.purchase_request_lines.request_id
            move.purchase_request_ids = requests
            move.purchase_request_count = len(requests)

    def action_view_purchase_requests(self):
        self.ensure_one()
        return self.purchase_request_ids._get_action_view_purchase_requests()
