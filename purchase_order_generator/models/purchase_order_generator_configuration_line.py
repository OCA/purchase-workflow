# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class PurchaseOrderGeneratorConfigurationLine(models.Model):
    _name = 'purchase.order.generator.configuration.line'
    _description = "Purchase Order Generator Configuration Line"

    configurator_id = fields.Many2one(
        'purchase.order.generator.configuration',
        'Configurator',
        required=True,
        ondelete='cascade',
        select=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True,
        help='The product that will be purchased'
    )
    quantity_ratio = fields.Float(
        'Quantity Ratio',
        required=True,
        help='The quantity of the purchase order line generated will be '
             'obtained by multiplying this ratio and an initial quantity '
             'defined in the wizard.'
    )
    sequence = fields.Integer(
        'Sequence',
        required=True,
        help='The planned date of the purchase order line generated will be '
             'obtained by adding sequence*interval days/weeks/months/years to '
             'the initial date.'
    )

    @api.constrains('quantity_ratio')
    def _check_quantity_positive(self):
        """
        Check if quantity ratio is positive
        """
        for record in self:
            if record.quantity_ratio < 0:
                raise ValidationError(
                    "Quantity ratio must be positive: %s"
                    % record.quantity_ratio
                )
