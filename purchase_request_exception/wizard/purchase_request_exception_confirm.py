# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseRequestExceptionConfirm(models.TransientModel):
    _name = "purchase.request.exception.confirm"
    _description = "Purchase request exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one("purchase.request", "Purchase request")

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.button_draft()
            self.related_model_id.ignore_exception = True
            self.related_model_id.button_to_approve()
        return super().action_confirm()
