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

from odoo import api, models
from odoo.exceptions import ValidationError


class ComputedPurchaseOrderLine(models.Model):
    _inherit = "computed.purchase.order.line"

    @api.constrains("purchase_qty_package")
    def _check_purchase_qty_package_max(self):
        for rec in self:
            max_nb_of_package = rec.psi_id.max_nb_of_package
            if max_nb_of_package > 0 and rec.purchase_qty_package > max_nb_of_package:
                product_name = rec.product_id.name
                product_disp_format = f"[{rec.product_code}] {product_name}"
                if not rec.product_code:
                    product_disp_format = f"{product_name}"
                raise ValidationError(
                    self.env._(
                        "Don't allow to change the number of package for "
                        "the product %s is greater than Max. Nb of Package configured: %s",  # noqa E501
                        product_disp_format,
                        max_nb_of_package,
                    )
                )
