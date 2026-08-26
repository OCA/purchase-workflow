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

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # Columns section
    min_nb_of_package = fields.Float(
        "Min. Nb of Package",
        digits="Product UoM",
        help="""The minimum number of package you have to buy to get"""
        """ the lowest price.""",
        default=0,
    )
    max_nb_of_package = fields.Float(
        "Max. Nb of Package",
        digits="Product UoM",
        help="""The maximum number of package you can buy.""",
    )
    min_qty = fields.Float(
        store=True,
        readonly=False,
        compute="_compute_min_qty",
    )

    @api.depends("min_nb_of_package", "package_qty")
    def _compute_min_qty(self):
        for rec in self:
            if rec.package_qty:
                rec.min_qty = rec.min_nb_of_package * rec.package_qty
            # Don't care the else case, because the min_qty is stored.

    @api.constrains("max_nb_of_package", "min_nb_of_package")
    def _check_nb_of_package_limit(self):
        for rec in self:
            if (
                rec.max_nb_of_package > 0
                and rec.max_nb_of_package < rec.min_nb_of_package
            ):
                raise ValidationError(
                    self.env._(
                        "Max. Nb of Package must be greater than Min. Nb of Package"
                    )
                )

    def _convert_qty(self, quantity):
        """
        Set the qty by max_nb_of_package
        """
        quantity = super()._convert_qty(quantity)
        if self.package_qty and self.max_nb_of_package > 0:
            max_quantity = self.max_nb_of_package * self.package_qty
            if quantity > max_quantity:
                quantity = max_quantity
        return quantity
