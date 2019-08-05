# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    discount2 = fields.Float(
        string='Discount 2 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount3 = fields.Float(
        string='Discount 3 (%)',
        digits=dp.get_precision('Discount'),
    )

    @api.onchange('name')
    def onchange_name(self):
        """Apply the default supplier discounts of the selected supplier"""
        for supplierinfo in self.filtered('name'):
            supplierinfo.discount2 = (
                supplierinfo.name.default_supplierinfo_discount2)
            supplierinfo.discount3 = (
                supplierinfo.name.default_supplierinfo_discount3)
        return super().onchange_name()

    @api.model
    def create(self, vals):
        """Insert discounts 2 and 3 from context from purchase.order's
        _add_supplier_to_product method"""
        if ('discount2_map' in self.env.context and
                not vals.get('discount2') and
                vals['product_tmpl_id'] in self.env.context['discount2_map']):
            vals['discount2'] = self.env.context['discount2_map'][
                vals['product_tmpl_id']]
        if ('discount3_map' in self.env.context and
                not vals.get('discount3') and
                vals['product_tmpl_id'] in self.env.context['discount3_map']):
            vals['discount3'] = self.env.context['discount3_map'][
                vals['product_tmpl_id']]
        return super(ProductSupplierInfo, self).create(vals)
