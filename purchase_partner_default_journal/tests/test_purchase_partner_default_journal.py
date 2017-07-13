# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from openerp.tests import common
from openerp.addons.account.tests.account_test_classes import AccountingTestCase

class TestPurchasePartnerDefaultJournal(AccountingTestCase):
    def test_purchase_partner_default_journal(self):
        p = self.env.ref('base.res_partner_1')
        # the installation should have found a journal
        self.assertTrue(p.default_purchase_journal_id)
        # check if changing this cascades to the children
        self.product_id_1 = self.env.ref('product.product_product_8')
	self.product_id_2 = self.env.ref('product.product_product_11')
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
        po_vals = {
            'partner_id': p.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT
                    ),
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                    'price_unit': 250.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT
                    ),
                })],
        }

	self.po = self.env['purchase.order'].create(po_vals)
        invoice = self.env['account.invoice'].with_context(
            type='in_invoice').create({
                'partner_id': p.id,
                'purchase_id': self.po.id,
                'account_id': p.property_account_payable_id.id,
	})
        # need to trigger onchange before journal is correct
        onchange = invoice._onchange_partner_id()
        # invoice onchange
        self.assertEqual(
            journal.id,
            onchange['value']['journal_id']
        )
