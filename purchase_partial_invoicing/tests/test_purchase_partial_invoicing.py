# -*- coding: utf-8 -*-
#
##############################################################################
#
#    Authors: Adrien Peiffer
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

from openerp.tests import common
from openerp import workflow
from openerp.tools.safe_eval import safe_eval


class testPurchasePartialInvoicing(common.TransactionCase):

    def setUp(self):
        super(testPurchasePartialInvoicing, self).setUp()
        # tests are called before register_hook
        self.env['ir.rule']._register_hook()
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

    def test_invoice_partial_po(self):
        self.common_test()
        line_to_invoice = self.purchase_order.order_line[0]
        ctx = self.context.copy()
        ctx.update({'active_ids': line_to_invoice.id})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if only the line that I chose is invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_lines), 1,
                         "Number of invoiced lines isn't correct")

    def test_invoice_partial_line(self):
        self.common_test()
        quantity_to_invoiced = 5
        line_to_invoice = self.purchase_order.order_line[0]
        ctx = self.context.copy()
        ctx.update({'active_ids': line_to_invoice.id})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I change the quantity on the line that will be invoiced
        wizard.line_ids[0].invoiced_qty = quantity_to_invoiced
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if only the line that I chose is invoiced
        invoice_line = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_line), 1,
                         "Number of invoiced lines isn't correct")
        # I check if the quantity on the invoice line is correct
        self.assertEqual(invoice_line.quantity, quantity_to_invoiced,
                         "Quantity on invoice line isn't correct")
        # I check invoiced quantity on the purchase order line
        self.assertEqual(line_to_invoice.invoiced_qty, invoice_line.quantity,
                         "Invoiced quantity isn't the same as on invoice line")
        # I change the quantity on the invoice line
        invoice_line.write({'quantity': quantity_to_invoiced - 1})
        # I check invoiced quantity on the purchase order line
        self.assertEqual(line_to_invoice.invoiced_qty, invoice_line.quantity,
                         "Invoiced quantity isn't the same as on invoice line")
        # I remove invoice line
        invoice_line.unlink()
        # I check invoiced quantity on the purchase order line
        self.assertEqual(line_to_invoice.invoiced_qty, 0,
                         "Invoiced quantity isn't the same as on invoice line")

    def test_invoiced_status(self):
        self.common_test()
        # I select a line to do a partial invoicing
        line_to_partial = self.purchase_order.order_line[0]
        # I create a wizard to invoiced all lines
        ctx = self.context.copy()
        ctx.update({'active_ids': self.purchase_order.order_line.ids})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I find the prepare line to invoiced
        prepare_line = self.env['purchase.order.line_invoice.line']\
            .search([('po_line_id', '=', line_to_partial.id),
                     ('wizard_id', '=', wizard.id)])
        # i check if I found a line
        self.assertEqual(len(prepare_line), 1,
                         "Number of prepare line isn't correct")
        # I change the quantity to invoice on this line
        prepare_line.invoiced_qty = line_to_partial.product_qty - 1
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if only the line that I chose is invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_lines), 1,
                         "Number of invoiced lines isn't correct")
        # I check if all lines are invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_lines), len(self.purchase_order),
                         "All of purchase lines aren't invoiced")
        # I check if the partial line is still present
        purchase_line_domain = self.po_line_obj.search(self.domain)
        self.assertEqual(len(purchase_line_domain), 1,
                         "Lines are still present")
        self.assertEqual(purchase_line_domain, line_to_partial,
                         "line on the menu isn't the same than invoiced line")
        # I get the created invoice
        invoice = invoice_lines[0].invoice_id
        # I validate the invoice
        workflow.trg_validate(self.uid, 'account.invoice',
                              invoice.id, 'invoice_open',
                              self.cr)
        # I check invoice's state
        self.assertEqual(invoice.state, 'open',
                         "invoice's state isn't correct")
        # I check if the partial line isn't flag as invoiced
        self.assertFalse(line_to_partial.invoiced)
        # I check if the purchase order isn't flag as invoiced
        self.assertFalse(self.purchase_order.invoiced)
        # I invoice the last line
        ctx = self.context.copy()
        ctx.update({'active_ids': line_to_partial.id})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if the lines are no longer on the menu
        purchase_line_domain = self.po_line_obj.search(self.domain)
        self.assertEqual(len(purchase_line_domain), 0,
                         "Lines are still present")
        # I check if the line is invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', '=', line_to_partial.id),
                     ('invoice_id.state', '=', 'draft')])
        self.assertEqual(len(invoice_lines), 1,
                         "Number of invoiced lines isn't correct")
        # I get the created invoice
        invoice = invoice_lines.invoice_id
        # I validate the invoice
        workflow.trg_validate(self.uid, 'account.invoice',
                              invoice.id, 'invoice_open',
                              self.cr)
        # I check invoice's state
        self.assertEqual(invoice.state, 'open',
                         "invoice's state isn't correct")
        # I check if the partial line is flag as invoiced
        self.assertTrue(line_to_partial.invoiced)
        # I check if the purchase order is flag as invoiced
        self.assertTrue(self.purchase_order.invoiced)

    def test_cancel_quantity(self):
        self.common_test()
        quantity_to_invoice = 4
        line_to_invoice = self.purchase_order.order_line[0]
        ctx = self.context.copy()
        ctx.update({'active_ids': line_to_invoice.id})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I change the quantity on the line that will be invoiced
        wizard.line_ids[0].invoiced_qty = quantity_to_invoice
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I cancel quantity
        quantity_to_cancel = 4
        wizard = self.env['purchase.order.line_cancel_quantity']\
            .with_context(ctx).create({})
        # I change the quantity on the line that will be cancelled
        wizard.line_ids[0].cancelled_qty = quantity_to_cancel
        wizard.cancel_quantity()
        # I check the cancelled quantity on purchase line
        self.assertEqual(line_to_invoice.cancelled_qty, quantity_to_cancel)
        # I check the quantity to invoiced
        max_quantity = line_to_invoice.product_qty -\
            line_to_invoice.invoiced_qty - line_to_invoice.cancelled_qty
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        self.assertEqual(wizard.line_ids[0].product_qty, max_quantity)
        # I make an invoice for the remaining quantity
        wizard.line_ids[0].invoiced_qty = max_quantity
        wizard.with_context(ctx).makeInvoices()
        # I check if the line is fully invoiced
        self.assertTrue(line_to_invoice.fully_invoiced)

    def test_cancel_full_line(self):
        self.common_test()
        line_to_cancel = self.purchase_order.order_line[0]
        lines_to_invoice = self.purchase_order.order_line\
            .filtered(lambda r: r.id != line_to_cancel.id)
        ctx = self.context.copy()
        ctx.update({'active_ids': lines_to_invoice.ids})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        ctx.update({'active_ids': line_to_cancel.id})
        # I check if lines are invoiced
        invoice_lines = self.inv_line_obj\
            .search([('purchase_line_id', 'in', lines_to_invoice.ids)])
        self.assertEqual(len(invoice_lines), len(lines_to_invoice.ids))
        # I get the created invoice
        invoice = invoice_lines[0].invoice_id
        # I validate the invoice
        workflow.trg_validate(self.uid, 'account.invoice',
                              invoice.id, 'invoice_open',
                              self.cr)
        # I cancel quantity
        quantity_to_cancel = line_to_cancel.product_qty
        wizard = self.env['purchase.order.line_cancel_quantity']\
            .with_context(ctx).create({})
        # I change the quantity on the line that will be cancelled
        wizard.line_ids[0].cancelled_qty = quantity_to_cancel
        wizard.cancel_quantity()
        # I check the cancelled quantity on purchase line
        self.assertEqual(line_to_cancel.cancelled_qty, quantity_to_cancel)
        # I check if the line is fully invoiced
        self.assertTrue(line_to_cancel.fully_invoiced)
        # I check if the purchase order is invoiced
        line_to_cancel.order_id.invalidate_cache()
        self.assertTrue(line_to_cancel.order_id.invoiced)

    def test_line_zero(self):
        self.common_test()
        quantity_to_invoiced = 0
        line_to_invoice = self.purchase_order.order_line[0]
        ctx = self.context.copy()
        ctx.update({'active_ids': line_to_invoice.id})
        wizard = self.env['purchase.order.line_invoice']\
            .with_context(ctx).create({})
        # I change the quantity on the line that will be invoiced
        wizard.line_ids[0].invoiced_qty = quantity_to_invoiced
        # I click on make invoice button
        wizard.with_context(ctx).makeInvoices()
        # I check if only the line that I chose is invoiced
        invoice_line = self.inv_line_obj\
            .search([('purchase_line_id', 'in', self.purchase_order.ids)])
        self.assertEqual(len(invoice_line), 1,
                         "Number of invoiced lines isn't correct")
        # I check if the quantity on the invoice line is correct
        self.assertEqual(invoice_line.quantity, quantity_to_invoiced,
                         "Quantity on invoice line isn't correct")
        # I check invoiced quantity on the purchase order line
        self.assertEqual(line_to_invoice.invoiced_qty, invoice_line.quantity,
                         "Invoiced quantity isn't the same as on invoice line")
