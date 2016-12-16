# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def onchange_company_id(
        self, company_id, part_id, type, invoice_line, currency_id
    ):
        result = super(AccountInvoice, self).onchange_company_id(
            company_id, part_id, type, invoice_line, currency_id
        )
        if 'journal_id' in result['value']:
            result['value'].pop('journal_id')
        return result

    @api.multi
    def onchange_partner_id(
        self, type, partner_id, date_invoice=False, payment_term=False,
        partner_bank_id=False, company_id=False
    ):
        result = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id
        )
        if partner_id and type == 'in_invoice':
            result['value'].update(
                journal_id=self.env['res.partner'].browse(partner_id)
                .default_purchase_journal_id.id
            )
        return result
