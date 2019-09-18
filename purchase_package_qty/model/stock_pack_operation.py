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

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    package_qty = fields.Float(
        'Package Qty',
        help="""The quantity of products in the supplier package.""")
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""",)
    qty_done = fields.Float("Done (uom)")
    qty_done_package = fields.Float(
        "Done (package)", help="""The number of packages you've received.""",
        digits_compute=dp.get_precision('Product Unit of Measure'))

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        if self.package_qty:
            self.qty_done_package = self.qty_done / self.package_qty

    @api.onchange('qty_done_package')
    def onchange_qty_done_package(self):
        if self.qty_done_package == int(self.qty_done_package):
            self.qty_done = self.package_qty * self.qty_done_package

    def product_id_change(
            self, cr, uid, ids, product_id, product_uom_id, product_qty,
            context=None):
        res = super(StockPackOperation, self).product_id_change(
            cr, uid, ids, product_id, product_uom_id, product_qty,
            context=None)
        picking_id = context.get("default_picking_id", False)
        picking = self.pool.get('stock.picking').browse(
            cr, uid, picking_id, context=context)
        partner = picking.partner_id
        if product_id and partner:
            product = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)
            for supplier in product.seller_ids:
                if supplier.name == partner:
                    if not res.get('value', False):
                        res['value'] = {}
                    res['value']['package_qty'] = supplier.package_qty
                break
        return res
