# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class PurchaseOrderReceivedByCategory(models.Model):
    _name = "purchase.order.received.by.category"
    _description = "Purchase Order Received by Category"

    order_id = fields.Many2one('purchase.order', required=True, ondelete='cascade')
    category_id = fields.Many2one('product.category', required=True)
    product_qty = fields.Float(string='Received Quantity')
    qty_received = fields.Float(string='To Receive Quantity')
    to_receive = fields.Float(string='Received Percentage')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchased_quantity_total = fields.Float(string='Total Quantity', compute='_compute_purchased_quantity_total')
    delivery_status = fields.Float(compute='_compute_delivery_status')
    received_by_category_ids = fields.One2many('purchase.order.received.by.category',
                                               'order_id', string='Received by Category',
                                               compute='_compute_received_by_category_ids')

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

    @api.depends('order_line.product_qty', 'order_line.qty_received')
    def _compute_received_by_category_ids(self):
        for order in self:
            received_by_category_obj = self.env['purchase.order.received.by.category']
            order.received_by_category_ids.unlink()
            received_by_category_ids = []
            for category in order.mapped('order_line.product_id.categ_id'):
                lines = order.order_line.filtered(lambda l: l.product_id.categ_id == category)
                if lines:
                    product_qty = sum(lines.mapped('product_qty'))
                    qty_received = sum(lines.mapped('qty_received'))
                    to_receive = sum(lines.mapped('to_receive'))
                    values = {
                        'order_id': order.id,
                        'category_id': category.id,
                        'product_qty': product_qty,
                        'qty_received': qty_received,
                        'to_receive': to_receive,
                    }
                    received_by_category_ids.append(received_by_category_obj.create(values).id)
            order.received_by_category_ids = received_by_category_ids



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    to_receive = fields.Float(compute='_compute_to_receive')

    @api.depends('product_qty', 'qty_received')
    def _compute_to_receive(self):
        for line in self:
            line.to_receive = line.product_qty - line.qty_received
