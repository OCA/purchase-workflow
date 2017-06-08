# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id2 = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract / Analytic',
        help='Use to store the value of project_id if there is no lines')
    project_id = fields.Many2one(
        compute='_compute_project_id',
        inverse='_inverse_project_id',
        comodel_name='account.analytic.account',
        string='Contract / Analytic', readonly=True,
        states={'draft': [('readonly', False)]},
        store=True,
        help="The analytic account related to a sales order.")

    @api.one
    @api.depends('order_line.account_analytic_id')
    def _compute_project_id(self):
        """ If all order line have same analytic account set project_id
        """
        al = self.project_id2
        if self.order_line:
            al = (self.order_line[0].account_analytic_id) or False
            for ol in self.order_line:
                if ol.account_analytic_id != al:
                    al = False
                    break
        self.project_id = al

    @api.one
    def _inverse_project_id(self):
        """ When set project_id set analytic account on all order lines
        """
        if self.project_id:
            self.order_line.write({'account_analytic_id': self.project_id.id})
        self.project_id2 = self.project_id

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """ When change project_id set analytic account on all order lines
            Do it in one operation to avoid to recompute the project_id field
            during the change.
            In case of new record, nothing is recomputed to avoid ugly message
        """
        r = []
        for ol in self.order_line:
            if isinstance(ol.id, int):
                r.append((1, ol.id,
                          {'account_analytic_id': self.project_id.id}))
            else:
                # this is new record, do nothing !
                return
        self.project_id2 = self.project_id
        self.order_line = r

    def _get_merge_order_key(self):
        res = super(PurchaseOrder, self)._get_merge_order_key()
        return res + ('project_id', )
