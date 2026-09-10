##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
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

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_product_base_line_for_taxes_computation(self, product_line):
        """Override to set quantity to nb of package if price policy is package."""
        self.ensure_one()
        if product_line.price_policy == "package":
            origin_quantiy = product_line.quantity
            product_line.with_context(
                check_move_validity=False
            ).quantity = product_line.product_qty_package
            res = super()._prepare_product_base_line_for_taxes_computation(product_line)
            product_line.with_context(
                check_move_validity=False
            ).quantity = origin_quantiy
            return res
        else:
            return super()._prepare_product_base_line_for_taxes_computation(
                product_line
            )
