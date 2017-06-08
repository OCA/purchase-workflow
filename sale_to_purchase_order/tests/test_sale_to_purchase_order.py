# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

import openerp.tests.common as common


class TestSaleToPurchaseOrder(common.TransactionCase):

    def setUp(self):
        super(TestSaleToPurchaseOrder, self).setUp()

    def test_procurement(self):
        """ Create sale order :
                * product.product_product_36
            Confirm sale order
            Check there is no po for the product_product_36
            Create sale order :
                * product.product_product_36
            Confirm and reorder sale order
            Check there is a po for the product_product_36
        """

        po_line_obj = self.env['purchase.order.line']
        po_line = po_line_obj.search(
            [('product_id', '=',
              self.env.ref('product.product_product_36').id)])
        po_line.order_id.signal_workflow("purchase_confirm")

        so1 = self.env['sale.order'].create(
            {'partner_id': self.env.ref('base.res_partner_3').id})
        self.env['sale.order.line'].create(
            {'order_id': so1.id,
             'product_id': self.env.ref('product.product_product_36').id})
        so1.action_button_confirm()
        po_line = po_line_obj.search(
            [('product_id', '=',
              self.env.ref('product.product_product_36').id),
             ('state', '=', 'draft')])
        self.assertEqual(0, len(po_line))
        self.assertEqual('manual', so1.state)

        so2 = self.env['sale.order'].create(
            {'partner_id': self.env.ref('base.res_partner_3').id})
        self.env['sale.order.line'].create(
            {'order_id': so2.id,
             'product_id': self.env.ref('product.product_product_36').id})
        proc_batch_gen_obj = self.env['procurement.batch.generator']
        proc_batch_gen = proc_batch_gen_obj.with_context(
            active_model='sale.order', active_id=so2.id,
            valid_so=True).create({})
        proc_batch_gen.validate()
        po_line = po_line_obj.search(
            [('product_id', '=',
              self.env.ref('product.product_product_36').id),
             ('state', '=', 'draft')])
        self.assertEqual(1, len(po_line))
        self.assertEqual('manual', so2.state)
