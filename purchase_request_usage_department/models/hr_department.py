# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    usage_id = fields.Many2one(
        comodel_name='purchase.product.usage',
        string="Default Usage",
        help="Default Usage for purchased products")
