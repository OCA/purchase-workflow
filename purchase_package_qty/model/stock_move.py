# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
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

from openerp import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    package_qty = fields.Float(
        'Package Qty', compute='_compute_package_qty',
        help="""The quantity of products in the supplier package.""")
    indicative_package = fields.Boolean('Indicative Package')
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""")

    # Constraints section
    # TODO: Rewrite me in _contraint, if the Orm V8 allows param in message.

    @api.multi
    @api.depends('product_id')
    def _compute_package_qty(self):
        for pol in self:
            if pol.product_id:
                for supplier in pol.product_id.seller_ids:
                    if pol.partner_id and (supplier.name == pol.partner_id):
                        pol.package_qty = supplier.package_qty

    # Views section
    def onchange_product_id(
            self, cr, uid, ids, product_id=False, loc_id=False,
            loc_dest_id=False, partner_id=False):
        res = super(StockMove, self).onchange_product_id(
            cr, uid, ids, prod_id=product_id)
        if product_id and partner_id:
            product = self.pool.get('product.product').browse(
                cr, uid, product_id)
            for supplier in product.seller_ids:
                if partner_id and (supplier.name.id == partner_id):
                    if not res.get('value', False):
                        res['value'] = {}
                    res['value']['package_qty'] = supplier.package_qty
                    res['value']['product_qty'] = supplier.package_qty
                    res['value']['product_qty_package'] = 1
                    res['value']['indicative_package'] =\
                        supplier.indicative_package
        return res

    def onchange_product_qty(
            self, cr, uid, ids, product_id, product_qty, product_uom,
            package_qty):
        res = super(StockMove, self).onchange_quantity()
        if package_qty:
            if not res.get('value', False):
                res['value'] = {}
            res['value']['product_qty_package'] = product_qty / package_qty
        return res

    @api.onchange('product_qty_package')
    def onchange_product_qty_package(self):
        if self.product_qty_package == int(self.product_qty_package):
            self.product_qty = self.package_qty * self.product_qty_package
