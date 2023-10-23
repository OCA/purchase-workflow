# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    branch_id = fields.Many2one(comodel_name="res.branch")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        active_ids = self.env.context.get("active_ids", False)
        _model = {
            "purchase.request.line": "",
            "purchase.request": "line_ids",
        }
        request_lines = (
            self.env[active_model].browse(active_ids).mapped(_model[active_model])
        )
        all_branch = [rec.branch_id.id for rec in request_lines.mapped("request_id")]
        if len(set(all_branch)) != 1:
            raise UserError(_("You cannot create RFQ with multi branch."))
        res["branch_id"] = request_lines[0].request_id.branch_id.id
        return res

    @api.model
    def _prepare_purchase_order(
        self, picking_type, group_id, company, currency, origin
    ):
        data = super()._prepare_purchase_order(
            picking_type, group_id, company, currency, origin
        )
        data["branch_id"] = self.branch_id.id
        return data
