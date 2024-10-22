# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    requested_employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Requested Employees",
        compute="_compute_requested_employee_ids",
        store=True,
    )

    @api.depends(
        "order_line.purchase_request_lines.requested_employee_id",
        "order_line.purchase_request_lines",
    )
    def _compute_requested_employee_ids(self):
        for rec in self:
            rec.requested_employee_ids = rec.order_line.mapped(
                "purchase_request_lines.requested_employee_id"
            )
