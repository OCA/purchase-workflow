# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestProcurementBatchGenerator(TransactionCase):

    def test_wizard(self):
        '''Create procurement requests, validate and check result'''
        pbgo = self.env['procurement.batch.generator']
        ctx = self.env.context.copy()
        ctx.update({
            'active_ids': [
                self.env.ref('product.product_product_25').id,
                self.env.ref('product.product_product_27').id],
            'active_model': 'product.product'})
        wiz = pbgo.with_context(ctx).create({})
        wiz.line_ids.write({'procurement_qty': 42})
        action = wiz.validate()
        proc_ids = action['domain'][0][2]
        self.assertEqual(len(proc_ids), 2)
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for proc in self.env['procurement.order'].browse(proc_ids):
            self.assertFalse(float_compare(
                proc.product_qty, 42, precision_digits=prec))
            self.assertIn(proc.state, ('running', 'exception'))
