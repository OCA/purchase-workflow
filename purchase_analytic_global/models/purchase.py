# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        states={'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]},
        help="The analytic account that will be set on all the lines. "
             "If you want to use different accounts, leave this field "
             "empty and set the accounts individually on the lines.")

    @api.onchange('account_analytic_id')
    def onchange_default_analytic_id(self):
        if not self.order_line:
            return
        for line in self.order_line:
            line.account_analytic_id = self.account_analytic_id
