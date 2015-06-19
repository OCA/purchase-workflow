# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_last_purchase(self):
        """
        Get last purchase price, last purchase date and last customer
        """
        for product in self:
            last_date = False
            last_price = False
            last_seller = False
            lines = self.env['purchase.order.line'].search(
                [('product_id', '=', product.id),
                 ('state', 'in', ['confirmed', 'done'])])
            if lines:
                old_lines = sorted(lines, key=lambda l: l.order_id.date_order,
                                   reverse=True)
                last_date = old_lines[0].order_id.date_order
                last_price = old_lines[0].price_unit
                last_seller = old_lines[0].order_id.partner_id
            product.last_purchase_date = last_date
            product.last_purchase_price = last_price
            product.last_seller = last_seller

    last_purchase_price = fields.Float(
        string='Last Purchase Price', compute=_get_last_purchase)
    last_purchase_date = fields.Date(
        string='Last Purchase Date', compute=_get_last_purchase)
    last_seller = fields.Many2one(
        comodel_name='res.partner', string='Last Seller',
        compute=_get_last_purchase)
