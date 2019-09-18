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

from openerp import api, models, fields
from openerp.addons import decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    package_qty = fields.Float(
        'Package Qty', digits_compute=dp.get_precision('Product UoM'),
        help="""The quantity of products in the supplier package."""
        """ You will always have to buy a multiple of this quantity.""",
        default=1)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = super(StockInventory, self)._get_inventory_lines(inventory)
        product_obj = self.env['product.product']
        new_val = []
        for val in vals:
            product_id = val['product_id']
            # if product_id == 47:
            #     import pdb; pdb.set_trace()
            product = self.env['product.product'].browse(product_id)
            seller = product_obj._select_seller(
                product_id=product, quantity=1)
            val['package_qty'] = seller.package_qty or 1
            new_val.append(val)
        return new_val
