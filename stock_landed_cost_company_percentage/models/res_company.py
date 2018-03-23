# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    landed_cost_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Landed Costs Journal',
    )
    landed_cost_company_line = fields.One2many(
        'landed.cost.company.line',
        'company_id',
        string='Landed Costs'
    )
