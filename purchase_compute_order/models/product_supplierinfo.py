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
from math import ceil

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # Columns Section
    shelf_life = fields.Integer(
        string="Shelf life (days)",
        inverse="_inverse_shelf_life",
    )

    def _inverse_shelf_life(self):
        for psi in self:
            lines = (
                self.env["computed.purchase.order.line"]
                .sudo()
                .search(
                    [
                        ("psi_id", "=", psi.id),
                    ]
                )
            )
            lines = lines.filtered(lambda line: line.cpo_state == "draft")
            for line in lines:
                line.shelf_life = psi.shelf_life

    def _convert_qty(self, quantity):
        """
        Round the quantity by package qty (contained qty in a package)
        """
        self.ensure_one()
        if self.package_qty and quantity % self.package_qty:
            quantity = ceil(quantity / self.package_qty) * self.package_qty
        return quantity
