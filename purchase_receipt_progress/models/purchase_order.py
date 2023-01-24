# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchased_quantity_total = fields.Float(string='Total Quantity', compute='_compute_purchased_quantity_total')
    delivery_status = fields.Float(compute='_compute_delivery_status')

    @api.depends('order_line.product_qty')
    def _compute_purchased_quantity_total(self):
        for order in self:
            order.purchased_quantity_total = sum(order.mapped('order_line.product_qty'))

    @api.depends('order_line.product_qty', 'order_line.qty_received')
    def _compute_delivery_status(self):
        for order in self:
            if order.purchased_quantity_total:
                order.delivery_status = sum(
                    order.mapped('order_line.qty_received')) / order.purchased_quantity_total * 100
            else:
                order.delivery_status = 0


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    to_receive = fields.Float(compute='_compute_to_receive')

    @api.depends('product_qty', 'qty_received')
    def _compute_to_receive(self):
        for line in self:
            line.to_receive = line.product_qty - line.qty_received
