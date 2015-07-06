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

from openerp import fields, models


class PurchaseOrderGenerator(models.TransientModel):
    _inherit = 'purchase.order.generator'

    analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='Analytic account that will be associated to each purchase order '
             'line.'
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
        values = super(PurchaseOrderGenerator, self).\
            get_purchase_order_line_values(
            configurator_line, date_planned, purchase_order)
        values['account_analytic_id'] = self.analytic_id.id
        return values
