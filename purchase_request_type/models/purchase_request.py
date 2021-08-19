# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def _default_request_type(self):
        return self.env["purchase.request.type"].search(
            [("company_id", "in", [False, self.env.company.id])],
            limit=1,
        )

    name = fields.Char(
        string="Request Reference",
        required=True,
        default="/",
        tracking=True,
    )
    request_type = fields.Many2one(
        comodel_name="purchase.request.type",
        string="PR Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
        default=lambda self: self._default_request_type(),
    )
    reduce_step = fields.Boolean(compute="_compute_request_type")

    @api.depends("request_type")
    def _compute_request_type(self):
        for obj in self:
            if obj.request_type:
                obj.reduce_step = obj.request_type.reduce_step
            else:
                obj.reduce_step = False

    @api.onchange("request_type")
    def onchange_request_type(self):
        for request in self:
            if request.request_type.picking_type_id:
                request.picking_type_id = request.request_type.picking_type_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/" and vals.get("request_type"):
            purchase_type = self.env["purchase.request.type"].browse(
                vals["request_type"]
            )
            if purchase_type and purchase_type.sequence_id:
                vals["name"] = purchase_type.sequence_id.next_by_id()
            else:
                vals["name"] = self.env["ir.sequence"].next_by_code("purchase.request")
        return super().create(vals)

    @api.constrains("company_id")
    def _check_pr_type_company(self):
        if self.filtered(
            lambda r: r.request_type.company_id
            and r.company_id
            and r.request_type.company_id != r.company_id
        ):
            raise ValidationError(_("Document's company and type's company mismatch"))

    @api.onchange("company_id")
    def _onchange_company(self):
        self.request_type = False
