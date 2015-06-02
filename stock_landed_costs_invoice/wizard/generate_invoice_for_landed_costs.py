# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
from openerp import models, fields, api, _


class LandedCostGenerateInvoice(models.TransientModel):
    '''generate the invoices for Landed costs.
    '''

    _name = 'landed.cost.generate.invoice'

    invoice_date = fields.Date('Invoice Date')

    @api.one
    def get_grouped_lines(self, cost_ids):
        '''get the grouped cost lines.
        @return: {'journal1': {'supplier1': [cost_line1, cost_line2, ... ]}}
        '''
        res = {}
        cost_obj = self.env['stock.landed.cost']
        costs = cost_obj.browse(cost_ids)
        costs_groups = costs.get_cost_group_by_journal()
        for journal_id, costs_group in costs_groups.items():
            res[journal_id] = {}
            # group by partner
            all_lines = []
            for cost in costs_group:
                all_lines += cost.cost_lines
            for line in all_lines:
                # filter out the lines which no need to create invoice for it.
                if not line.generate_invoice:
                    continue
                if not res[journal_id].get(line.partner_id.id):
                    res[journal_id][line.partner_id.id] = []
                res[journal_id][line.partner_id.id].append(line)
        return res

    @api.one
    def _get_inv_name(self, lines):
        costs = {}
        for l in lines:
            costs[l.cost_id] = True
        inv_name = ' - '.join([cost.name for cost in costs.keys()])
        return inv_name

    @api.one
    def get_account_id_for_cost_line(self, cost_line):
        '''get the account_id for the cost line when preparing the invoice line
        data'''
        # when we don't have the account assigned on the cost line,
        # we should get it from the journal id on the cost.
        # OR get it from the expense account from the product.
        account_id = cost_line.account_id and cost_line.account_id.id or False
        if not account_id:
            product = cost_line.product_id
            account = product.property_account_expense or \
                product.categ_id.property_account_expense_categ
            account_id = account and account.id
        assert account_id, 'You must configure the '
        'expense account for the product %s' % product.name
        return account_id

    def prepare_inv_line(self,
                         cost_lines, context=None):
        """ Collects require data from landed cost line that is used to
        create invoice line.

        :param cost_lines: record sets of landed cost lines
        :return: Value for fields of invoice lines.
        :rtype: dict

        """
        invoice_lines = []
        for cost_line in cost_lines:
            # get the right account
            account_id = self.get_account_id_for_cost_line(cost_line)

            # get the tax from supplier
            line_tax_ids = [
                x.id for x in cost_line.product_id.supplier_taxes_id]
            invoice_lines.append(
                (0, 0, {
                    'name': cost_line.product_id.name,
                    'account_id': account_id and account_id[0],
                    'price_unit': cost_line.price_unit or 0.0,
                    'quantity': 1,
                    'product_id': cost_line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, line_tax_ids)],
                }))
        return invoice_lines

    def _get_currency_id(self, journal_id):
        '''get the currency when creating invoice for the landed cost lines

        first get from the journal, if no currency, then we use the currency
        from current user company'''
        journal_obj = self.env['account.journal']
        journal = journal_obj.browse(journal_id)
        currency_id = journal.currency and journal.currency.id or False
        if not currency_id:
            # TODO case: multi currency of one company
            currency_id = self.env.user.company_id.currency_id.id
        return currency_id

    @api.one
    def _generate_invoice_per_cost_lines_group(
            self, lines, partner_id, journal_id, invoice_date=None):
        '''Generate the invoice for the grouped cost lines.'''
        invoice_obj = self.env['account.invoice']
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(partner_id)
        # prepare the invoice lines data
        line_data = self.prepare_inv_line(lines)
        invoice_id = invoice_obj.create(
            {
                'name': self._get_inv_name(lines),
                'origin': self._get_inv_name(lines),
                'date_invoice': invoice_date,
                'user_id': self.env.user.id,
                'partner_id': partner_id,
                'journal_id': journal_id,
                'account_id': partner.property_account_payable.id,
                'type': 'in_invoice',
                'currency_id': self._get_currency_id(journal_id),
                'invoice_line': line_data
            })
        return invoice_id

    @api.one
    def make_invoices(self):
        invoice_ids = []
        cost_ids = self.env.context.get('active_ids')
        # get grouped lines to be for invoicing.
        grouped_lines = self.get_grouped_lines(cost_ids)
        if not grouped_lines:
            return False
        # TODO why grouped_lines is a list.
        for journal_id, partner_lines_group in grouped_lines[0].items():
            for partner_id, lines in partner_lines_group.items():
                # generate the invoices for every cost lines group
                invoice_id = self._generate_invoice_per_cost_lines_group(
                    lines, partner_id=partner_id, journal_id=journal_id,
                    invoice_date=self.invoice_date)
                invoice_ids.append(invoice_id)
            self.invoice_creationg_hook()
        domain = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
        return {
            'domain': domain,
            'name': _('Landed Cost Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }
