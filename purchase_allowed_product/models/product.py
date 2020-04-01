# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        use_only_supplied_product = self.env.context.get(
            'use_only_supplied_product')
        if use_only_supplied_product:
            restrict_supplier_id = self.env.context.get('restrict_supplier_id')
            seller = self.env['res.partner'].browse(restrict_supplier_id)
            seller = seller.commercial_partner_id \
                if seller.commercial_partner_id else seller
            supplierinfos = self.env['product.supplierinfo'].search(
                [('name', '=', seller.id)])
            args += [
                '|',
                ('product_tmpl_id', 'in',
                    [x.product_tmpl_id.id for x in supplierinfos]),
                ('id', 'in',
                    [x.product_id.id for x in supplierinfos])]

        return super(ProductProduct, self).search(
            args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args += [
                ('name', operator, name)
            ]
        tasks = self.search(args, limit=limit)
        return tasks.name_get()
