# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class RequestRequest(models.Model):
    _inherit = "request.request"

    use_pr = fields.Boolean(related="category_id.use_pr")
    purchase_request_count = fields.Integer(compute="_compute_purchase_request_count")
    purchase_request_ids = fields.One2many(
        string="Purchase Requests",
        comodel_name="purchase.request",
        inverse_name="ref_request_id",
        copy=False,
    )

    def _ready_to_submit(self):
        if not super()._ready_to_submit():
            return False
        if not self.purchase_request_ids:
            return True
        if self.purchase_request_ids.filtered_domain(
            [("state", "not in", ["rejected", "to_approve"])]
        ):
            return False
        return True

    def _compute_purchase_request_count(self):
        for request in self:
            request.purchase_request_count = len(request.purchase_request_ids)
