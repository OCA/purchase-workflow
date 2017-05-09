# coding: utf-8
# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def add_product(self):
        self.ensure_one()
        action = self.env.ref('quick_purchase.product_product_action')
        context = ast.literal_eval(action.context or "{}").copy()
        context.update({'purchase_id': self.id})
        result = action.read()[0]
        name = action.name + " (%s)" % self.partner_id.name
        result.update(
            {'target': 'current', 'context': context,
             'view_mode': 'tree', 'name': name})
        return result
