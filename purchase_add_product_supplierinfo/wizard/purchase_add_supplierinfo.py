# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class PurchaseAddProductSupplierinfo(models.TransientModel):
    _name = 'purchase.add.product.supplierinfo'

    wizard_line_ids = fields.One2many(
        'purchase.add.product.supplierinfo.line',
        'wizard_id',
        string='Wizard lines')

    @api.multi
    def add_product_supplierinfo(self):
        purchase = self.env['purchase.order'].browse(
            self._context['active_id'])
        purchase.signal_workflow('purchase_confirm')
        if purchase.partner_id.commercial_partner_id:
            supplier_id = purchase.partner_id.commercial_partner_id
        else:
            supplier_id = purchase.partner_id
        for line in self.wizard_line_ids:
            vals = {
                'name': supplier_id.id,
                'min_qty': 0.0,
                'delay': 1,
            }
            if line.to_variant:
                vals.update({
                    'product_id': line.product_id.id,
                })
            else:
                vals.update({
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                })
            self.env['product.supplierinfo'].create(vals)

    @api.multi
    def purchase_confirm(self):
        purchase = self.env['purchase.order'].browse(
            self._context['active_id'])
        purchase.signal_workflow('purchase_confirm')


class PurchaseAddProductSupplierinfoLine(models.TransientModel):
    _name = 'purchase.add.product.supplierinfo.line'

    wizard_id = fields.Many2one(
        'purchase.add.product.supplierinfo',
        string='Wizard Reference')
    name = fields.Text(string='Description', required=True)
    product_id = fields.Many2one('product.product',
                                 string='Product')
    to_variant = fields.Boolean(string='Added to the variant',
                                help="if option is checked then supplier is "
                                     "added to the product variant else "
                                     "supplier is added to the "
                                     "product template")
