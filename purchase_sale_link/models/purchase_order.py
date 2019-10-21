# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_count = fields.Integer(
        string='Sale Orders',
        compute='_compute_sale_order_count',
    )

    @api.model
    def get_purchase_sale_action_xmlid(self):
        return 'sale.action_orders'

    @api.model
    def get_purchase_sale_form_view_xmlid(self):
        return 'sale.view_order_form'

    @api.multi
    def get_sale_orders(self):
        self.ensure_one()

        # Catch the Sale Orders related to the actual Purchase Order
        # from the procurement_groups related to the stock_moves
        # created from the Purchase Order (only valid for Sale Orders with
        # storable products)
        stock_moves = self.order_line.mapped('move_dest_ids')
        procurement_groups = stock_moves.mapped('group_id')
        sale_orders = procurement_groups.mapped('sale_id')

        # Add the Sale Orders linked with the actual Purchase Order via
        # service products
        sale_orders |= self.order_line.mapped('sale_order_id')

        return sale_orders

    @api.multi
    def action_view_sale_order(self):
        sale_orders = self.get_sale_orders()

        action_xmlid = self.get_purchase_sale_action_xmlid()
        action = self.env.ref(action_xmlid).read()[0]
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        else:
            view_xmlid = self.get_purchase_sale_form_view_xmlid()
            action['views'] = [(self.env.ref(view_xmlid).id, 'form')]
            action['res_id'] = sale_orders.id
        return action

    @api.depends('order_line.move_dest_ids')
    def _compute_sale_order_count(self):
        for order in self:
            sale_orders = order.get_sale_orders()
            order.sale_order_count = len(sale_orders)
