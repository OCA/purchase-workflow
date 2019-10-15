# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import api, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.onchange('department_id')
    def onchange_department_id(self):
        for line in self.line_ids:
            line.usage_id = self.department_id.usage_id
