##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class UpdateProductsWizard(models.TransientModel):
    _name = 'update.products.wizard'
    _description = 'Update product_supplierinfo from compute_purchase_order'

    # Columns Section
    line_ids = fields.One2many(
        'update.products.line.wizard',
        'wizard_id', 'Updated Products list')

    # Overload section
    @api.model
    def default_get(self, fields):
        line_ids = []
        res = super(UpdateProductsWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id', False)
        if active_id:
            psi_obj = self.env['product.supplierinfo']
            cpo = self.env['computed.purchase.order'].browse(active_id)
            cpol = cpo.line_ids.filtered(lambda l: l.state == 'updated')
            for line in cpol:
                psi = psi_obj.search([
                    ('name', '=',
                        line.computed_purchase_order_id.partner_id.id),
                    ('product_tmpl_id', '=',
                        line.product_id.product_tmpl_id.id)
                ])

                line_ids.append((0, 0, {
                    'product_id': line.product_id.id,
                    'supplierinfo_id': psi.id,
                    'product_code': line.product_code,
                    'product_name': line.product_name,
                    'product_uom': line.uom_po_id.id,
                    'package_qty': line.package_qty,
                    'price': line.product_price,
                    'discount': line.discount,
                    'computed_purchase_order_line_id': line.id,
                }))
        res.update({'line_ids': line_ids})
        return res

    # Action section
    @api.multi
    def apply_product_change(self):
        cpol = self.env['computed.purchase.order.line']
        for upw in self:
            for line in upw.line_ids:
                values = {
                    'product_name': line.product_name,
                    'product_code': line.product_code,
                    'product_uom': line.product_uom.id,
                    'package_qty': line.package_qty,
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    'price': line.price,
                    'discount': line.discount,
                }
                line.supplierinfo_id.write(values)
                cpol |= line.computed_purchase_order_line_id
        return cpol.write({'state': 'up_to_date'})


class UpdateProductsLineWizard(models.TransientModel):
    _name = "update.products.line.wizard"
    _description = "Information about products to update"

    # Columns section
    wizard_id = fields.Many2one(
        'update.products.wizard', 'Wizard Reference', index=True)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True, ondelete='cascade',
        index=True)
    supplierinfo_id = fields.Many2one(
        'product.supplierinfo', 'Partner Information', required=True,
        ondelete='cascade')
    product_code = fields.Char(
        'Supplier Product Code', size=64,
        help="""This supplier's product code will be used when printing"""
        """ a request for quotation. Keep empty to use the internal"""
        """ one.""")
    product_name = fields.Char(
        'Supplier Product Name', size=128,
        help="""This supplier's product name will be used when printing"""
        """ a request for quotation. Keep empty to use the internal"""
        """ one.""")
    product_uom = fields.Many2one(
        'uom.uom', 'Supplier Unit of Measure', required=True,
        help="""This comes from the product form.""")
    package_qty = fields.Float(
        'Package Quantity', required=True,
        help="""The minimal quantity to purchase to this supplier,"""
        """ expressed in the supplier Product Unit of Measure if not"""
        """ empty, in the default unit of measure of the product"""
        """ otherwise.""")
    price = fields.Float(
        'Unit Price', required=True,
        digits=dp.get_precision('Product Price'),
        help="""This price will be considered as a price for the"""
        """ supplier Unit of Measure if any or the default Unit of"""
        """ Measure of the product otherwise""")
    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'))
    computed_purchase_order_line_id = fields.Many2one(
        'computed.purchase.order.line', 'Compute Line', required=True,
        ondelete='cascade', index=True)
