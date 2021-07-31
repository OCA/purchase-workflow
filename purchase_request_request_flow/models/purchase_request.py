# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseRquest(models.Model):
    _name = "purchase.request"
    _inherit = ["purchase.request", "request.doc.mixin"]
    _request_freeze_states = ["pending"]
    _doc_approved_states = ["approved"]

    # --------------------------------------------
    # Default values pass to PR
    # --------------------------------------------

    def _prepare_defaults(self):
        res = super()._prepare_defaults()
        request = self.ref_request_id
        lines = []
        for line in request.product_line_ids:
            vals = {
                "product_id": line.product_id.id,
                "name": line.description,
                "product_qty": line.quantity,
                "estimated_cost": line.price_subtotal,
            }
            lines.append((0, 0, vals))
        res.update(
            {
                "origin": request.name,
                "requested_by": request.requested_by.id,
                "assigned_to": request.approver_id.id,
                "date_start": request.date or fields.Date.context_today(self),
                "description": request.reason,
                "line_ids": lines,
            }
        )
        return res

    # --------------------------------------------
    # Server Actions after PR Action
    # --------------------------------------------

    def button_approved(self):
        res = super().button_approved()
        for rec in self.filtered("ref_request_id"):
            rec._run_doc_action("approved")
        return res

    def button_rejected(self):
        res = super().button_rejected()
        for rec in self.filtered("ref_request_id"):
            rec._run_doc_action("rejected")
        return res


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _inherit = ["purchase.request.line", "request.doc.line.mixin"]

    ref_request_id = fields.Many2one(
        related="request_id.ref_request_id",
    )

    # --------------------------------------------
    # Values from request, when create new PR line
    # --------------------------------------------

    def _prepare_defaults(self):
        res = super()._prepare_defaults()
        return res
