# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_product_supplierinfo_domain(self, product_id):
        return [('product_id', '=', product_id.id),
                ('name', '=', self.partner_id.id)]

    @api.model
    def _check_product_supplierinfo(self):
        products = []
        for line in self.order_line:
            domain = self._get_product_supplierinfo_domain(line.product_id)
            result = self.env['product.supplierinfo'].search(domain)
            if not result:
                products.append(line.product_id.id)
        return products

    @api.multi
    def purchase_confirm(self):
        self.ensure_one()
        self.wkf_confirm_order()
        products_to_update = []
        products_to_update = self._check_product_supplierinfo()
        if products_to_update:
            ctx = dict(
                default_supplier_id=self.partner_id.id,
                default_product_ids=[(6, 0, products_to_update)],
            )
            add_supplierinfo_form = self.env.ref(
                'purchase_add_product_supplierinfo.'
                'view_purchase_add_supplierinfo_form', False)
            return {
                'name': _('Associate the products and the supplier '
                          'of this purchase order.'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.add.product.supplierinfo',
                'views': [(add_supplierinfo_form.id, 'form')],
                'view_id': add_supplierinfo_form.id,
                'target': 'new',
                'context': ctx,
            }

    #@api.multi
    #def purchase_approve(self):
    #    self.ensure_one()
    #    self.wkf_approve_order()
    #    products_to_update = []
    #    products_to_update = self._check_product_supplierinfo()
    #    if products_to_update:
    #        ctx = dict(
    #            default_supplier_id=self.partner_id.id,
    #            default_product_ids=[(6, 0, products_to_update)],
    #        )
    #        add_supplierinfo_form = self.env.ref(
    #            'purchase_add_product_supplierinfo.'
    #            'view_purchase_add_supplierinfo_form', False)
    #        return {
    #            'name': _('Associate the products and the supplier '
    #                      'of this purchase order.'),
    #            'type': 'ir.actions.act_window',
    #            'view_type': 'form',
    #            'view_mode': 'form',
    #            'res_model': 'purchase.add.product.supplierinfo',
    #            'views': [(add_supplierinfo_form.id, 'form')],
    #            'view_id': add_supplierinfo_form.id,
    #            'target': 'new',
    #            'context': ctx,
    #        }
