# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    @api.depends('order_line.account_analytic_id')
    def _compute_analytic_accounts(self):
        res = {}
        for purchase in self:
            res[purchase.id] = []
            for po_line in purchase.order_line:
                if po_line.account_analytic_id:
                    res[purchase.id].append(po_line.account_analytic_id.id)
        return res

    @api.model
    def _search_analytic_accounts(self, operator, value):
        po_line_obj = self.env['purchase.order.line']
        res = []
        po_lines = po_line_obj.search(
            [('account_analytic_id', operator, value)])
        order_ids = [po_line.order_id and po_line.order_id.id for po_line in
                     po_lines]
        res.append(('id', 'in', order_ids))
        return res

    account_analytic_ids = \
        fields.Many2many(comodel_name='account.analytic.account',
                         string='Analytic Account',
                         compute='_compute_analytic_accounts',
                         search='_search_analytic_accounts',
                         readonly=True)
