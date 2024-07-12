# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requisition_count = fields.Integer(
        compute="_compute_requisition_count",
    )

    def _compute_requisition_count(self):
        for rec in self:
            rec.requisition_count = len(
                rec.mapped("line_ids.requisition_lines.requisition_id")
            )

    def action_view_purchase_requisition(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_requisition.action_purchase_requisition"
        )
        requisitions = self.mapped("line_ids.requisition_lines.requisition_id")
        if len(requisitions) == 1:
            action["res_id"] = requisitions.id
            action["views"] = [
                (
                    self.env.ref(
                        "purchase_requisition.view_purchase_requisition_form"
                    ).id,
                    "form",
                )
            ]
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", requisitions.ids)]

        action["context"] = {}
        return action


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.depends("purchase_lines")
    def _compute_is_editable(self):
        res = super(PurchaseRequestLine, self)._compute_is_editable()
        editable_records = self.filtered(lambda p: p in self and p.requisition_lines)
        editable_records.write({"is_editable": False})
        return res

    def _compute_requisition_qty(self):
        for rec in self:
            requisition_qty = 0.0
            req_lines = rec.requisition_lines.filtered(
                lambda l: l.requisition_id.state != "cancel"
            )
            for req_line in req_lines:
                requisition_qty += req_line.product_qty
            rec.requisition_qty = requisition_qty

    @api.depends("requisition_lines.requisition_id.state")
    def _compute_requisition_state(self):
        for rec in self:
            temp_req_state = False
            if rec.requisition_lines:
                if any(
                    [
                        pr_line.requisition_id.state == "done"
                        for pr_line in rec.requisition_lines
                    ]
                ):
                    temp_req_state = "done"
                elif all(
                    [
                        pr_line.requisition_id.state == "cancel"
                        for pr_line in rec.requisition_lines
                    ]
                ):
                    temp_req_state = "cancel"
                elif any(
                    [
                        pr_line.requisition_id.state == "in_progress"
                        for pr_line in rec.requisition_lines
                    ]
                ):
                    temp_req_state = "in_progress"
                elif all(
                    [
                        pr_line.requisition_id.state in ("draft", "cancel")
                        for pr_line in rec.requisition_lines
                    ]
                ):
                    temp_req_state = "draft"
            rec.requisition_state = temp_req_state

    requisition_lines = fields.Many2many(
        "purchase.requisition.line",
        "purchase_request_purchase_requisition_line_rel",
        "purchase_request_line_id",
        "purchase_requisition_line_id",
        string="Purchase Agreement Lines",
        readonly=True,
        copy=False,
    )
    requisition_qty = fields.Float(
        compute="_compute_requisition_qty", string="Quantity in a Bid"
    )
    requisition_state = fields.Selection(
        compute="_compute_requisition_state",
        string="Bid Status",
        type="selection",
        selection=lambda self: self.env["purchase.requisition"]
        ._fields["state"]
        .selection,
        store=True,
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", string="Is editable")

    def unlink(self):
        if self.filtered("requisition_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        return super().unlink()
