# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestPurchasePartnerDefaultJournal(TransactionCase):
    def test_purchase_partner_default_journal(self):
        p = self.env.ref('base.res_partner_1')
        # the installation should have found a journal
        self.assertTrue(p.default_purchase_journal_id)
        # check if changing this cascades to the children
        journal = self.env['account.journal'].create({
            'name': 'default purchase journal',
            'code': 'def',
            'type': 'purchase',
        })
        p.default_purchase_journal_id = journal

        self.assertEqual(
            self.env.ref('base.res_partner_address_1')
            .default_purchase_journal_id,
            journal,
        )
        # invoice onchange
        onchange = self.env['account.invoice'].onchange_company_id(
            p.company_id.id, p.id, 'in_invoice', False, False
        )
        self.assertTrue('journal_id' not in onchange['value'])
        onchange = self.env['account.invoice'].onchange_partner_id(
            'in_invoice', p.id
        )
        self.assertEqual(
            journal.id,
            onchange['value']['journal_id']
        )
        # invoice created from order
        values = self.env['purchase.order'].onchange_dest_address_id(
            p.id
        )['value']
        values['partner_id'] = p.id
        invoice_data = self.env['purchase.order']._prepare_invoice(
            self.env['purchase.order'].create(values), []
        )
        self.assertEqual(journal.id, invoice_data['journal_id'])
