# -*- coding: utf-8 -*-
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

from openerp import api, fields, models, tools
from dateutil.relativedelta import relativedelta
from datetime import datetime


class PurchaseOrderGenerator(models.TransientModel):
    _name = 'purchase.order.generator'
    _description = 'Purchase Order Generator'

    date = fields.Date(
        string='Date',
        required=True,
        help='Initial date to which we apply the time deltas defined in the '
             'configurator.'
    )
    configurator_id = fields.Many2one(
        comodel_name='purchase.order.generator.configuration',
        string='Configuration Model',
        required=True,
        help='Configuration Model that will be used to generate purchase '
             'order lines.'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        required=True,
        help='Supplier of the purchase order which will be generated.'
    )
    initial_quantity = fields.Integer(
        string='Initial Quantity',
        required=True,
        help='Initial quantity used to compute each purchase order line '
             'quantities. It is multiplied by the ratios defined in the '
             'configurator.'
    )
    destination_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination Location',
        required=True,
        help='Where the products will be transferred.'
    )

    def get_purchase_order_line_values(self, configurator_line, date_planned,
                                       purchase_order):
        """
        Return values necessary to create a purchase order line
        :param configurator_line: the purchase order generator configuration
        line
        :param date_planned: the date_planned for that line
        :param purchase_order: the related purchase order
        """
        return {
            'order_id': purchase_order.id,
            'product_id': configurator_line.product_id.id,
            'name': configurator_line.product_id.name,
            'date_planned': date_planned,
            'product_qty':
                configurator_line.quantity_ratio * self.initial_quantity,
            'price_unit': 0.0,
        }

    @api.multi
    def validate(self):
        """
        Generate a purchase order.
        Each purchase order line is computed thanks to the model configured
        as a purchase.order.generator.configuration.
        """
        initial_date = datetime.strptime(self.date,
                                         tools.DEFAULT_SERVER_DATE_FORMAT)

        purchase_order_pool = self.env['purchase.order']
        purchase_order_line_pool = self.env['purchase.order.line']
        po = purchase_order_pool.create({
            'origin': self.configurator_id.name,
            'partner_id': self.partner_id.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'location_id': self.destination_location_id.id,
            'configurator_id': self.configurator_id.id,
        })

        for configurator_line in self.configurator_id.line_ids:
            period = self.configurator_id.interval * configurator_line.sequence
            if self.configurator_id.recurrence_type == 'daily':
                delta = relativedelta(days=period)
            elif self.configurator_id.recurrence_type == 'weekly':
                delta = relativedelta(weeks=period)
            elif self.configurator_id.recurrence_type == 'monthly':
                delta = relativedelta(months=period)
            else:
                delta = relativedelta(years=period)
            date_planned = initial_date + delta
            purchase_order_line_pool.create(
                self.get_purchase_order_line_values(
                    configurator_line,
                    date_planned,
                    po
                )
            )

        return {'type': 'ir.actions.act_window_close'}
