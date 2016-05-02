# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class PurchaseAddProductSupplierinfo(models.TransientModel):
    _name = 'purchase.add.product.supplierinfo'
    _description = "Update Product Sellers from Purchase Order"

    product_ids = fields.Many2many('product.product',
                                   string='Products')

    @api.multi
    def add_product_supplierinfo(self):
        order = self.env['purchase.order'].browse(
            self._context['active_id'])
        order.signal_workflow('purchase_confirm')
        if order.partner_id.parent_id:
            supplier_id = order.partner_id.parent_id
        else:
            supplier_id = order.partner_id
        for product in self.product_ids:
            self.env['product.supplierinfo'].create({
                'name': supplier_id.id,
                'product_id': product.id,
                'min_qty': 0.0,
                'delay': 1,
            })
