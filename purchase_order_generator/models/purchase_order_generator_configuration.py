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

from openerp import api, models, fields


class PurchaseOrderGeneratorConfiguration(models.Model):
    _name = 'purchase.order.generator.configuration'
    _description = "Purchase Order Generator Configuration"

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
        copy=False,  # Prevent duplicate from copying the translation
    )
    interval = fields.Integer(
        'Repeat every',
        required=True,
        default=1,
        help='A purchase order line will be generated every x '
             'days/weeks/months/years (x is the interval).'
    )
    recurrence_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('yearly', 'Year(s)')],
        'Recurrence Type',
        default='weekly',
        help='A purchase order line will be generated every x '
             'days/weeks/months/years (x is the interval).'
    )
    line_ids = fields.One2many(
        'purchase.order.generator.configuration.line',
        'configurator_id',
        'Purchase Order Generator Configuration Lines',
        copy=True,
    )

    _sql_constraints = [
        ('name_unique',
         'unique(name)',
         'The configurator name must be unique !')
    ]

    @api.one
    def copy(self, default=None):
        """Override unique name by appending Copy to it

        If there is already a copied element, add a count in the name.
        """
        if default is None:
            default = {}
        nb = self.search_count(
            [('name', 'like', "%s - " % self.name)])
        new_name = "%s - %d" % (self.name, nb + 1)
        default.update({'name': new_name})
        return super(PurchaseOrderGeneratorConfiguration, self).copy(default)
