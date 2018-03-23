# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LandedCostCompanyLine(models.Model):
    _name = 'landed.cost.company.line'
    _description = 'Landed Cost Company Line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Landed Cost',
        domain=[('landed_cost_ok', '=', True)],
        required=True
    )
    percentage = fields.Float(string='Percentage')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
