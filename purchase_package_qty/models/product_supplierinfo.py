##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    # Columns section
    package_qty = fields.Float(
        'Package Qty', digits=dp.get_precision('Product UoM'),
        help="""The quantity of products in the supplier package."""
        """ You will always have to buy a multiple of this quantity.""",
        default=1)
    indicative_package = fields.Boolean(
        'Indicative Package',
        help="""If checked, the system will not force you to purchase"""
        """ a strict multiple of package quantity""",
        default=False)
    price_policy = fields.Selection(
        [('uom', 'per UOM'), ('package', 'per Package')], "Price Policy",
        default='uom', required=True)
    base_price = fields.Float(
        'Price', required=False, default=0.00,
        digits=dp.get_precision('Product Price'),
        help="The price to purchase a product")
    price = fields.Float(
        "Price per Unit", compute='_compute_price',
        required=False, store=True, readonly=True)

    @api.depends('base_price', 'price_policy', 'package_qty')
    @api.multi
    def _compute_price(self):
        for psi in self:
            if psi.price_policy == 'package':
                if psi.package_qty == 0:
                    psi.package_qty = 1
                psi.price = psi.base_price / psi.package_qty
            else:
                psi.price = psi.base_price

    @api.model
    def create(self, vals):
        if not vals.get('base_price', False):
            if vals.get('price', False):
                vals['base_price'] = vals['price']
                del vals['price']
            else:
                vals['base_price'] = 0
        res = super(ProductSupplierinfo, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if not vals.get('base_price', False):
            if vals.get('price', False):
                vals['base_price'] = vals['price']
                del vals['price']
        return super(ProductSupplierinfo, self).write(vals)

    # Constraints section
    @api.multi
    @api.constrains('package_qty')
    def _check_package_qty(self):
        for psi in self:
            if psi.package_qty == 0:
                raise ValueError(_('The package quantity cannot be 0.'))

    # Init section
    @api.model
    def _init_package_qty(self):
        psi_ids = self.sudo().search([])
        for psi in psi_ids:
            vals = {}
            if not psi.package_qty:
                vals['package_qty'] = max(psi.min_qty, 1)
            if not psi.base_price:
                vals['base_price'] = psi.price
            if vals:
                psi.write(vals)
        return psi_ids.ids
