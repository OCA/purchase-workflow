# -*- coding: utf-8 -*-
#
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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
#


from openerp.tests import common
from openerp import workflow
from openerp.tools.safe_eval import safe_eval


class testPurchasePartialInvoicing(common.TransactionCase):

    def setUp(self):
        super(testPurchasePartialInvoicing, self).setUp()
        self.context = self.env['res.users'].context_get()
        self.po_obj = self.env['purchase.order']
        self.po_line_obj = self.env['purchase.order.line']
        self.inv_line_obj = self.env['account.invoice.line']

    def common_test(self):
        self.purchase_order = self.env.ref('purchase.purchase_order_1')
        # I change invoice method to 'based on purchase order line'
        self.purchase_order.invoice_method = 'manual'
        # I change the quantity on the first line to 10
        self.purchase_order.order_line[0].product_qty = 10
        # I confirm the purchase order
        workflow.trg_validate(self.uid, 'purchase.order',
                              self.purchase_order.id, 'purchase_confirm',
                              self.cr)
        # I check if the purchase order is confirmed
        self.purchase_order.invalidate_cache()
        self.assertEqual(self.purchase_order.state, 'approved',
                         "Purchase order's state isn't correct")
        # I get lines to invoiced
        purchase_lines = self.purchase_order.order_line
        # I get menu item action
        menu = self.env.ref('purchase.purchase_line_form_action2')
        self.domain = safe_eval(menu.domain)
        self.domain.extend([('order_id', '=', self.purchase_order.id),
                            ('fully_invoiced', '=', False)])
        purchase_line_domain = self.po_line_obj.search(self.domain)
        # I check if all lines is on the view's result
        self.assertEqual(purchase_line_domain, purchase_lines,
                         "lines aren't on the menu")

    def test_invoice_complete_po(self):
        self.common_test()
        # I create the wizard to invoiced lines
        ctx = self.context.copy()
        ctx.update({'active_ids': self.purchase_order.order_line.ids})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if all lines are invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_lines), len(self.purchase_order),
                         "All of purchase lines aren't invoiced")
        # I check if the lines are no longer on the menu
        purchase_line_domain = self.po_line_obj.search(self.domain)
        self.assertEqual(len(purchase_line_domain), 0,
                         "Lines are still present")
        for line in invoice_lines:
            self.assertEqual(line.sequence, line.purchase_line_id.sequence,
                             "Not same sequence")
