# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requisition_count = fields.Integer(
        compute="_compute_requisition_count",
    )

    @api.depends("line_ids.requisition_lines.requisition_id")
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
            action["view_mode"] = "list,form"
            action["domain"] = [("id", "in", requisitions.ids)]

        action["context"] = {}
        return action


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    requisition_lines = fields.Many2many(
        comodel_name="purchase.requisition.line",
        relation="purchase_request_purchase_requisition_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_requisition_line_id",
        string="Purchase Agreement Lines",
        readonly=True,
        copy=False,
    )
    requisition_qty = fields.Float(
        compute="_compute_requisition_qty", string="Quantity in a Bid"
    )
    requisition_state = fields.Selection(
        selection=lambda self: self.env["purchase.requisition"]
        ._fields["state"]
        .selection,
        compute="_compute_requisition_state",
        string="Bid Status",
        store=True,
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", string="Is editable")

    @api.depends("purchase_lines")
    def _compute_is_editable(self):
        res = super()._compute_is_editable()
        editable_records = self.filtered(lambda line: line.requisition_lines)
        editable_records.write({"is_editable": False})
        return res

    @api.depends(
        "requisition_lines.requisition_id.state", "requisition_lines.product_qty"
    )
    def _compute_requisition_qty(self):
        for rec in self:
            rec.requisition_qty = sum(
                [
                    req_line.product_qty or 0.0
                    for req_line in rec.requisition_lines
                    if req_line.requisition_id.state != "cancel"
                ]
            )

    @api.depends("requisition_lines.requisition_id.state")
    def _compute_requisition_state(self):
        for rec in self:
            states = set(rec.requisition_lines.mapped("requisition_id.state"))
            if not states:
                temp_req_state = False
            elif "done" in states:
                temp_req_state = "done"
            elif "confirmed" in states:
                temp_req_state = "confirmed"
            elif states == {"cancel"}:
                temp_req_state = "cancel"
            elif states.issubset({"draft", "cancel"}):
                temp_req_state = "draft"
            else:
                temp_req_state = False
            rec.requisition_state = temp_req_state

    def unlink(self):
        if self.filtered("requisition_lines"):
            raise UserError(
                self.env._("You cannot delete a record that refers to purchase lines!")
            )
        return super().unlink()
