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


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    package_qty = fields.Float(
        'Package Qty',
        help="""The quantity of products in the supplier package.""")
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""")
    price_policy = fields.Selection(
        [('uom', 'per UOM'), ('package', 'per Package')], "Price Policy",
        default='uom', required=True)

    @api.onchange('quantity')
    def onchange_product_qty(self):
        if self.package_qty:
            self.product_qty_package = self.quantity / self.package_qty

    @api.onchange('product_qty_package')
    def onchange_product_qty_package(self):
        if self.product_qty_package == int(self.product_qty_package):
            self.quantity = self.package_qty * self.product_qty_package

    @api.one
    @api.depends(
        'price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_qty_package', 'product_id', 'invoice_id.partner_id',
        'invoice_id.currency_id', 'invoice_id.company_id', 'price_policy')
    def _compute_price(self):
        line_qty = self.quantity

        # Use Product Qty Package for computation if price policy is not UOM
        if self.price_policy != 'uom':
            self.quantity = self.product_qty_package

        super(AccountInvoiceLine, self)._compute_price()

        # Restore the value of quantity
        if self.price_policy != 'uom':
            self.quantity = line_qty
