# -*- coding: utf-8 -*-
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
from openerp import models, fields


class PurchaseExpenseType(models.Model):
    _name = "purchase.expense.type"
    _description = "Purchase cost type"

    name = fields.Char(string='Name', required=True, translate=True,
                       select=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=(lambda self: self.env['res.company']._company_default_get(
            'purchase.cost.type')))
    default_expense = fields.Boolean(
        string='Default Expense',
        help="Specify if the expense will be automatically added in a "
             "purchase cost distribution.")
    calculation_method = fields.Selection(
        [('amount', 'By amount of the line'),
         ('price', 'By product price'),
         ('qty', 'By product quantity'),
         ('weight', 'By product weight'),
         ('weight_net', 'By product weight net'),
         ('volume', 'By product volume'),
         ('equal', 'Equally to all lines')], string='Calculation method',
        default='amount')
    note = fields.Text(string='Cost documentation')
    default_amount = fields.Float(
        string="Default amount",
        help="If set, this amount is put in the expense line when you "
             "select this expense type")
