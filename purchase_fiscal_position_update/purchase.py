# -*- coding: utf-8 -*-
#############################################################################
#
#    Purchase Fiscal Position Update module for Odoo
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Mathieu Vatel <mathieu _at_ julius.fr>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, api, _


class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.onchange('fiscal_position')
    def fiscal_position_change(self):
        '''Function executed by the on_change on the fiscal_position field
        of a purchase order ; it updates taxes on all order lines'''
        res = {'value': {}}
        lines_without_product = []
        if self.order_line:
            for line in self.order_line:
                fp = self.fiscal_position
                if line.product_id:
                    taxes = line.product_id.supplier_taxes_id
                    if fp:
                        taxes = fp.map_tax(taxes)
                    line.taxes_id = [(6, 0, taxes.ids)]
                else:
                    lines_without_product.append(line.name)

        if lines_without_product:
            res['warning'] = {'title': _('Warning')}
            if len(lines_without_product) == len(self.order_line):
                res['warning']['message'] = _(
                    "The Purchase Order Lines were not updated to the new "
                    "Fiscal Position because they don't have Products.\n"
                    "You should update the Taxes of each "
                    "Purchase Order Line manually.")
            else:
                res['warning']['message'] = _(
                    "The following Purchase Order Lines were not updated "
                    "to the new Fiscal Position because they don't have a "
                    "Product:\n- %s\nYou should update the "
                    "Taxes of these Purchase Order Lines manually."
                    ) % ('\n- '.join(lines_without_product))
        return res
