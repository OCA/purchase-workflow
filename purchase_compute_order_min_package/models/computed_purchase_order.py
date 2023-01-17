##############################################################################
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


class ComputedPurchaseOrder(models.Model):
    _inherit = 'computed.purchase.order'

    def parse_cpol_vals(self, psi, product):
        res = super(ComputedPurchaseOrder, self).parse_cpol_vals(psi, product)
        res.update({
            "purchase_qty_package": psi.min_nb_of_package
        })
        return res

    def parse_qty(self, cpo_line, days):
        quantity, product_price, psi_obj0, package_qty = super(ComputedPurchaseOrder, self).\
            parse_qty(cpo_line, days)
        
        purchase_qty_package = quantity / package_qty
        max_qty = 0
        if purchase_qty_package > 0 and purchase_qty_package != cpo_line.purchase_qty_package:
            psi_obj = cpo_line.get_psi(purchase_qty_package, operator='>=',
                order='min_nb_of_package')
            if psi_obj:
                quantity = psi_obj.min_nb_of_package * package_qty
            else:
                # Try to find the best psi
                psi_obj = cpo_line.get_psi(purchase_qty_package)
            if psi_obj:
                psi_obj0 = psi_obj
                package_qty = psi_obj.package_qty
                #quantity = psi_obj.min_nb_of_package * package_qty
                product_price = psi_obj.base_price
                max_qty = psi_obj.max_nb_of_package * package_qty
        if max_qty > 0 and quantity > max_qty:
            quantity = max_qty
        return quantity, product_price, psi_obj0, package_qty
