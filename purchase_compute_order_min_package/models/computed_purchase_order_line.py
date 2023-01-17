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
from odoo.exceptions import ValidationError


class ComputedPurchaseOrderLine(models.Model):
    _inherit = 'computed.purchase.order.line'

    def get_psi(self, purchase_qty_package=None, operator='<=', order='min_nb_of_package DESC'):
        if purchase_qty_package is None:
            purchase_qty_package = self.purchase_qty_package
        args = [
            ('name', '=', self.computed_purchase_order_id.partner_id.id),
            "|",
            ("product_id", "=", self.product_id.id),
            ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
            ("min_nb_of_package", operator, purchase_qty_package),
        ]
        psi = self.env["product.supplierinfo"].sudo().search(args, order=order, limit=1)
        return psi

    @api.onchange('purchase_qty_package')
    def onchange_purchase_qty_package(self):
        psi = self.get_psi()
        if psi:
            max_nb_of_package = psi.max_nb_of_package
        else:
            max_nb_of_package = self.psi_id.max_nb_of_package
        if not max_nb_of_package:
            return
        if self.purchase_qty_package > max_nb_of_package:
            product_disp_format = "[{supplier_code}] {product_name}"
            if not self.product_code_inv:
                product_disp_format = "{product_name}"
            
            raise ValidationError(_("Don't allow to change the number of package for "
                "the product {product} is greater than Max. Nb of Package configured: {max_nb}"
            ).format(product=product_disp_format.format(
                supplier_code=self.product_code_inv,
                product_name=self.product_id.name
                ),
                max_nb=max_nb_of_package
            ))
