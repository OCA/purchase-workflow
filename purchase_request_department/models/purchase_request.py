# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def _get_my_department(self):
        employees = self.env.user.employee_ids

        return (employees[0].department_id if employees
                else self.env['hr.department'])

    department_id = fields.Many2one('hr.department', 'Department',
                                    default=_get_my_department)

    @api.onchange('requested_by')
    def onchange_requested_by(self):
        employees = self.requested_by.employee_ids
        self.department_id = (employees[0].department_id if employees
                              else self.env['hr.department'])


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    department_id = fields.Many2one(
        comodel_name='hr.department',
        related='request_id.department_id',
        store=True,
        string='Department', readonly=True)
