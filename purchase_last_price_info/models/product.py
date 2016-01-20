# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_last_purchase(self):
        """ Get last purchase price, last purchase date and last supplier """
        for product in self:
            lines = self.env['purchase.order.line'].search(
                [('product_id', '=', product.id),
                 ('state', 'in', ['confirmed', 'done'])]).sorted(
                key=lambda l: l.order_id.date_order, reverse=True)
            product.last_purchase_date = lines[:1].order_id.date_order
            product.last_purchase_price = lines[:1].price_unit
            product.last_supplier_id = lines[:1].order_id.partner_id

    @api.multi
    def _set_last_purchase_price(self):
        """ set last purchase price, last purchase date and last supplier """
        for product in self:
            line = self.env['purchase.order.line'].search(
                [('product_id', '=', product.id),
                 ('state', 'in', ['confirmed', 'done'])]).sorted(
                key=lambda l: l.order_id.date_order, reverse=True)[:1]
            if line.order_id.partner_id and (
                    line.order_id.partner_id != product.last_supplier_id):
                product.last_supplier_id = line.order_id.partner_id
            if line.price_unit and(
                    line.price_unit != product.last_purchase_price):
                product.last_purchase_price = line.price_unit
            last_date = fields.Date.from_string(line.order_id.date_order)
            if line.order_id.date_order and (
                    fields.Date.to_string(last_date) !=
                    product.last_purchase_date):
                product.last_purchase_date = line.order_id.date_order

    last_purchase_price = fields.Float(
        string='Last Purchase Price', compute='_get_last_purchase',
        inverse='_set_last_purchase_price', store=True)
    last_purchase_date = fields.Date(
        string='Last Purchase Date', compute='_get_last_purchase',
        inverse='_set_last_purchase_price', store=True)
    last_supplier_id = fields.Many2one(
        comodel_name='res.partner', string='Last Supplier',
        compute='_get_last_purchase', inverse='_set_last_purchase_price',
        store=True)
