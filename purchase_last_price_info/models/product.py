# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _compute_last_purchase(self):
        """ Get last purchase price, last purchase date and last supplier """
        for product in self:
            line = self.env['purchase.order.line'].search([
                ('product_id', '=', self.id),
                ('state', 'in', ['purchase', 'done'])
            ], order='date_order DESC', limit=1)
            product.last_purchase_date = line.date_order
            product.last_purchase_price = line.price_unit
            product.last_supplier_id = line.partner_id

    last_purchase_price = fields.Float(
        string='Last Purchase Price',
        compute='_compute_last_purchase',
        digits=dp.get_precision('Product Price')
    )
    last_purchase_date = fields.Date(
        string='Last Purchase Date',
        compute='_compute_last_purchase'
    )
    last_supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Last Supplier',
        compute='_compute_last_purchase'
    )
