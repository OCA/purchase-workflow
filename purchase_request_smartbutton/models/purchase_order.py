# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_request_ids = fields.Many2many(
        comodel_name="purchase.request",
        string="Purchase Requests",
        compute="_compute_purchase_request_ids",
        help="Requests this order was raised for.",
    )
    purchase_request_count = fields.Integer(
        compute="_compute_purchase_request_ids",
    )

    @api.depends("order_line.purchase_request_lines.request_id")
    def _compute_purchase_request_ids(self):
        for order in self:
            requests = order.order_line.purchase_request_lines.request_id
            order.purchase_request_ids = requests
            order.purchase_request_count = len(requests)

    def action_view_purchase_requests(self):
        self.ensure_one()
        return self.purchase_request_ids._get_action_view_purchase_requests()
