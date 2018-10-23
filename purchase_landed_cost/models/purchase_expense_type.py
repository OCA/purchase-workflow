# Copyright 2013 Joaquín Gutierrez
# Copyright 2014-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class PurchaseExpenseType(models.Model):
    _name = "purchase.expense.type"
    _description = "Purchase cost type"

    name = fields.Char(string='Name', required=True, translate=True,
                       index=True)
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
         ('volume', 'By product volume'),
         ('equal', 'Equally to all lines')], string='Calculation method',
        default='amount',
    )
    note = fields.Text(string='Cost documentation')
    default_amount = fields.Float(
        string="Default amount",
        help="If set, this amount is put in the expense line when you "
             "select this expense type",
    )
