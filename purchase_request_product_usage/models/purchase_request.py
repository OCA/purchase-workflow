# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    usage_id = fields.Many2one(
        comodel_name='purchase.product.usage',
        string="Usage")

    @api.onchange('usage_id')
    def onchange_usage_id(self):
        if self.usage_id.product_id and not self.product_id:
            self.product_id = self.usage_id.product_id
