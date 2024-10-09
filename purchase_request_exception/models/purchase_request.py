# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseRequest(models.Model):
    _inherit = ["purchase.request", "base.exception"]
    _name = "purchase.request"
    _order = "main_exception_id asc, id desc"

    @api.model
    def test_all_draft_requests(self):
        request_set = self.search([("state", "=", "draft")])
        request_set.detect_exceptions()
        return True

    @api.model
    def _reverse_field(self):
        return "purchase_request_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped("line_ids")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "line_ids", "state")
    def purchase_request_check_exception(self):
        requests = self.filtered(lambda s: s.state == "to_approve")
        if requests:
            requests._check_exception()

    @api.onchange("line_ids")
    def onchange_ignore_exception(self):
        if self.state == "to_approve":
            self.ignore_exception = False

    def button_to_approve(self):
        if self.detect_exceptions() and not self.ignore_exception:
            return self._popup_exceptions()
        return super().button_to_approve()

    def button_draft(self):
        res = super().button_draft()
        for request in self:
            request.exception_ids = False
            request.main_exception_id = False
            request.ignore_exception = False
        return res

    @api.model
    def _get_popup_action(self):
        action = self.env.ref(
            "purchase_request_exception.action_purchase_request_exception_confirm"
        )
        return action
