# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tools import file_open
import base64


class TestUblOrderImport(TransactionCase):

    def test_ubl_order_import(self):
        tests = {
            'quote-PO00004.pdf': {
                'po_to_update': self.env.ref('purchase.purchase_order_4'),
                'incoterm': self.env.ref('stock.incoterm_DDU'),
                },
            }
        poio = self.env['purchase.order.import']
        for filename, res in tests.iteritems():
            po = res['po_to_update']

            f = file_open(
                'purchase_order_import_ubl/tests/files/' + filename, 'rb')
            quote_file = f.read()
            wiz = poio.with_context(
                active_model='purchase.order', active_id=po.id).create({
                    'quote_file': base64.b64encode(quote_file),
                    'quote_filename': filename,
                })
            f.close()
            self.assertEqual(wiz.purchase_id, po)
            wiz.update_rfq_button()
            self.assertEqual(po.incoterm_id, res['incoterm'])
