# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requested_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        default=lambda self: self.env.user.employee_id,
    )


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    requested_employee_id = fields.Many2one(
        related="request_id.requested_employee_id",
        store=True,
    )
