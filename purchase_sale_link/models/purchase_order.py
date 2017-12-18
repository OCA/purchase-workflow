# -*- coding: utf-8 -*-
# © 2017 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import models, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_purchase_sale_action_xmlid(self):
        return 'sale.action_orders'

    @api.model
    def get_purchase_sale_form_view_xmlid(self):
        return 'sale.view_order_form'

    @api.multi
    def action_view_sale_order(self):
        self.ensure_one()
        procurements = self.order_line.mapped('procurement_ids')
        procurement_group = procurements.mapped('group_id')
        sale_orders = self.env['sale.order'].search(
            [('procurement_group_id', 'in', procurement_group.ids)])
        if not sale_orders:
            raise exceptions.Warning(_('No sale order found'))

        action_xmlid = self.get_purchase_sale_action_xmlid()
        action = self.env.ref(action_xmlid).read()[0]
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        else:
            view_xmlid = self.get_purchase_sale_form_view_xmlid()
            action['views'] = [(self.env.ref(view_xmlid).id, 'form')]
            action['res_id'] = sale_orders.id
        return action
