# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'))

    @api.onchange('name')
    @api.multi
    def onchange_name(self):
        """ Apply the default supplier discount of the selected supplier """
        for supplierinfo in self.filtered('name'):
            supplierinfo.discount =\
                supplierinfo.name.default_supplierinfo_discount

    @api.model
    def create(self, vals):
        """ Insert discount from context from purchase.order's
        _add_supplier_to_product method """
        if ('discount_map' in self.env.context and
                not vals.get('discount') and
                vals['product_tmpl_id'] in self.env.context['discount_map']):

            vals['discount'] = self.env.context['discount_map'][
                vals['product_tmpl_id']]
        return super(ProductSupplierInfo, self).create(vals)
