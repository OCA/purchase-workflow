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
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    # Columns section
    min_nb_of_package = fields.Float(
        'Min. Nb of Package', digits=dp.get_precision('Product UoM'),
        help="""The minimum number of package you have to buy to get"""
        """ the lowest price.""",
        default=0)
    max_nb_of_package = fields.Float(
        'Max. Nb of Package', digits=dp.get_precision('Product UoM'),
        help="""The maximum number of package you can buy.""")

    @api.onchange("min_nb_of_package")
    def onchange_min_nb_of_package(self):
        self.min_qty = self.min_nb_of_package * self.package_qty

    @api.constrains('max_nb_of_package', 'min_nb_of_package')
    def _check_nb_of_package_limit(self):
        if self.max_nb_of_package > 0 and \
                self.max_nb_of_package < self.min_nb_of_package:
            raise ValidationError(_(
                "Max. Nb of Package must be greater than Min. Nb of Package"
            ))
