# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.one
    def _get_last_purchase(self):
        """ Get last purchase price, last purchase date and last supplier """
        lines = self.env['purchase.order.line'].search(
            [('product_id', '=', self.id),
             ('state', 'in', ['confirmed', 'done'])]).sorted(
            key=lambda l: l.order_id.date_order, reverse=True)
        self.last_purchase_date = lines[:1].order_id.date_order
        self.last_purchase_price = lines[:1].price_unit
        self.last_supplier_id = lines[:1].order_id.partner_id

    last_purchase_price = fields.Float(
        string='Last Purchase Price', compute='_get_last_purchase')
    last_purchase_date = fields.Date(
        string='Last Purchase Date', compute='_get_last_purchase')
    last_supplier_id = fields.Many2one(
        comodel_name='res.partner', string='Last Supplier',
        compute='_get_last_purchase')
