# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    partner_id = fields.Many2one('res.partner', 'Landed cost supplier')

    @api.multi
    def get_cost_group_by_journal(self):
        '''get grouped lc by journal.
        :return: {journal1: [id1, id2], journal2: [id1, id2, ...]...}'''

        res = {}
        for lc in self:
            assert lc.account_journal_id, 'You have to '
            'assign journal on Landed Cost %s' % lc.name
            if not res.get(lc.account_journal_id.id):
                res[lc.account_journal_id.id] = []
            res[lc.account_journal_id.id].append(lc)
        return res

    @api.multi
    def _generate_invoice_from_landed_cost(self):
        '''generate the invoice for a grouped landed costs.'''
        pass


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    generate_invoice = fields.Boolean(
        'Invoice?', default=True, help="To generate invoice or not.")

    # TODO, here we add a new field which is required to an existing table
    # should have a migration script
    partner_id = fields.Many2one(
        'res.partner',
        string='Landed cost supplier',
        readonly=False, required=True)

    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice')
