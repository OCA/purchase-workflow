# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestUblOrder(TransactionCase):

    def test_ubl_generate(self):
        ro = self.registry['report']
        poo = self.env['purchase.order']
        buo = self.env['base.ubl']
        order_states = poo.get_order_states()
        rfq_states = poo.get_rfq_states()
        for i in range(6):
            i += 1
            order = self.env.ref('purchase.purchase_order_%d' % i)
            # I didn't manage to make it work with new api :-(
            pdf_file = ro.get_pdf(
                self.cr, self.uid, order.ids,
                'purchase.report_purchasequotation')
            res = buo.get_xml_files_from_pdf(pdf_file)
            if order.state in order_states:
                filename = order.get_ubl_filename('order')
                self.assertTrue(filename in res)
            elif order.state in rfq_states:
                filename = order.get_ubl_filename('rfq')
                self.assertTrue(filename in res)
