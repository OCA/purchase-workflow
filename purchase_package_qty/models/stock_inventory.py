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

from odoo import api, models, fields
from odoo.addons import decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    package_qty = fields.Float(
        'Package Qty', digits=dp.get_precision('Product UoM'),
        help="""The quantity of products in the supplier package."""
        """ You will always have to buy a multiple of this quantity.""",
        default=1)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def _get_inventory_lines_values(self):
        vals = super(StockInventory, self)._get_inventory_lines_values()
        product_obj = self.env['product.product']
        new_val = []
        for val in vals:
            product_id = val['product_id']
            product = product_obj.browse(product_id)
            # seller = product._select_seller(quantity=1)
            seller = product.default_seller_id
            val['package_qty'] = seller.package_qty or 1
            new_val.append(val)
        return new_val
