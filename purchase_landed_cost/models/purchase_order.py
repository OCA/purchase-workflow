# -*- coding: utf-8 -*-
# © 2013 Joaquín Gutierrez
# © 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('purchase_id', '=', self.id)])
        if lines:
            mod_obj = self.env['ir.model.data']
            model, action_id = tuple(
                mod_obj.get_object_reference(
                    'purchase_landed_cost',
                    'action_purchase_cost_distribution'))
            action = self.env[model].browse(action_id).read()[0]
            ids = set([x.distribution.id for x in lines])
            if len(ids) == 1:
                res = mod_obj.get_object_reference(
                    'purchase_landed_cost', 'purchase_cost_distribution_form')
                action['views'] = [(res and res[1] or False, 'form')]
                action['res_id'] = list(ids)[0]
            else:
                action['domain'] = "[('id', 'in', %s)]" % list(ids)
            return action
