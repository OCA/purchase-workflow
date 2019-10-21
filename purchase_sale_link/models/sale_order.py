# © 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_count = fields.Integer(
        string="Number of Purchase Order",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user',
    )

    @api.multi
    def get_purchase_orders_service(self):
        """Get the Purchase Orders linked to one Sale Order
        by service products purchased automatically"""
        self.ensure_one()

        purchase_order_lines_service = self.env['purchase.order.line']\
            .search([('sale_order_id', 'in', self.ids)])

        purchase_orders_service = \
            purchase_order_lines_service.mapped('order_id')

        return purchase_orders_service

    @api.multi
    def get_purchase_orders_stock(self):
        """Get the Purchase Orders linked to one Sale Order
        by storable products purchased by 'Make To Order' route"""
        self.ensure_one()

        # Get the related stock moves via the SO's procurement_group_id
        procurement_group_id = self.procurement_group_id.id
        stock_moves = self.env['stock.move'].search([
            ('group_id', '=', procurement_group_id),
            ('created_purchase_line_id', '!=', 'False'),
        ])

        purchase_order_lines_stock = stock_moves\
            .mapped('created_purchase_line_id')
        purchase_orders_stock = purchase_order_lines_stock.mapped('order_id')

        return purchase_orders_stock

    @api.multi
    @api.depends('order_line.purchase_line_ids')
    def _compute_purchase_order_count(self):
        """
        Overwrite the original _compute_purchase_order_count() method in
        sale_purchase/models/sale_order.py

        The purchase_orders created from a service product are catched
        in this module in a diferent way from the original module.
        In this actual way, it allows to easily count and show purchase_orders
        from both storable and service products
        """
        for order in self:
            if order.state not in ('draft', 'sent'):
                purchase_orders = order.get_purchase_orders_service()
                purchase_orders |= order.get_purchase_orders_stock()
                order.purchase_order_count = len(purchase_orders)

    @api.model
    def get_sale_purchase_action_xmlid(self):
        return 'purchase.purchase_rfq'

    @api.model
    def get_sale_purchase_form_view_xmlid(self):
        return 'purchase.purchase_order_form'

    @api.multi
    def action_view_purchase(self):
        """Overwrite the original action_view_purchase() method in
        sale_purchase/models/sale_order.py"""
        purchase_orders = self.get_purchase_orders_service()
        purchase_orders |= self.get_purchase_orders_stock()

        action_xmlid = self.get_sale_purchase_action_xmlid()
        action = self.env.ref(action_xmlid).read()[0]

        if len(purchase_orders) > 1:
            action['domain'] = [('id', 'in', purchase_orders.ids)]
        else:
            view_xmlid = self.get_sale_purchase_form_view_xmlid()
            action['views'] = [(self.env.ref(view_xmlid).id, 'form')]
            action['res_id'] = purchase_orders.id

        return action
