# Copyright 2017-2020 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    def _get_my_department(self):
        employees = self.env.user.employee_ids
        return (
            employees[0].department_id
            if employees
            else self.env["hr.department"] or False
        )

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        default=lambda self: self._get_my_department(),
    )

    @api.onchange("requested_by")
    def onchange_requested_by(self):
        employees = self.requested_by.employee_ids
        self.department_id = employees[:1].department_id


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    department_id = fields.Many2one(
        comodel_name="hr.department",
        related="request_id.department_id",
        store=True,
        string="Department",
        readonly=True,
    )
