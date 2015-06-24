# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Therp BV (<http://therp.nl>)
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
import time
from openerp.tests.common import SingleTransactionCase
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATEFMT


class TestResetInvoiceMethod(SingleTransactionCase):
    wf_service = netsvc.LocalService("workflow")

    def setUp(self):
        """
        Create a supplier and a product.
        """
        self.supplier_id = self.registry('res.partner').create(
            self.cr, self.uid, {'name': 'Supplier', 'supplier': True})
        self.product_id = self.registry('product.product').create(
            self.cr, self.uid, {
                'name': 'Product test reset invoice method',
                'type': 'product',
                'supply_method': 'buy',
                'standard_price': 1.0,
                })

    def assert_state(self, po, state):
        self.assertTrue(
            po.state == state,
            'Purchase order is not in state \'%s\'' % state)

    def pay_invoice(self, po):
        """
        Pay the purchase order's first invoice with a voucher.
        This only affects the purchase order workflow in the case
        of invoice_method 'order'.
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        try:
            voucher_obj = reg('account.voucher')
        except KeyError:
            # Voucher module not available
            return
        voucher_context = {
            'payment_expected_currency': po.invoice_ids[0].currency_id.id,
            'default_partner_id': po.invoice_ids[0].partner_id.id,
            'default_amount': po.invoice_ids[0].residual,
            'default_reference': po.invoice_ids[0].name,
            'invoice_type': po.invoice_ids[0].type,
            'invoice_id': po.invoice_ids[0].id,
            'default_type': 'payment',
            'type': 'payment',
            }
        journal_id = reg('account.journal').search(
            cr, uid, [
                ('type', '=', 'bank'),
                ('company_id', '=', po.company_id.id)])[0]
        voucher_values = {
            'partner_id': po.invoice_ids[0].partner_id.id,
            'journal_id': journal_id,
            'account_id': reg('account.journal').browse(
                cr, uid, journal_id).default_credit_account_id.id,
            }
        voucher_values.update(voucher_obj.onchange_journal(
            cr, uid, False, voucher_values['journal_id'],
            [], False, po.invoice_ids[0].partner_id.id,
            time.strftime(DATEFMT), po.invoice_ids[0].residual,
            'payment', po.invoice_ids[0].currency_id.id,
            context=voucher_context)['value'])
        voucher_values['line_dr_ids'] = [
            (0, 0, line) for line in voucher_values['line_dr_ids']]
        voucher_id = voucher_obj.create(
            cr, uid, voucher_values, context=voucher_context)
        self.wf_service.trg_validate(
            uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)

        # Invoice has been paid and the purchase order is done
        po.refresh()
        self.assertTrue(
            po.invoice_ids[0].state == 'paid',
            'Did not succeed in paying the invoice with a voucher')
        return voucher_id

    def create_order(self, invoice_method):
        """
        Create a purchase order
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        po_pool = reg('purchase.order')
        line_pool = reg('purchase.order.line')
        line_values = {
            'product_id': self.product_id,
            'product_qty': 1,
            }
        line_values.update(
            line_pool.onchange_product_id(
                cr, uid, False, False, self.product_id,
                1, False, self.supplier_id)['value'])
        po_values = {
            'partner_id': self.supplier_id,
            'order_line': [(0, 0, line_values)],
            'invoice_method': invoice_method,
            }
        po_values.update(po_pool.onchange_dest_address_id(
            cr, uid, False, self.supplier_id)['value'])
        po_values.update(po_pool.onchange_partner_id(
            cr, uid, False, self.supplier_id)['value'])
        return po_pool.create(cr, uid, po_values)

    def create_invoice_from_pickings(self, picking_ids):
        """
        Receive a single invoice for all pickings.
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        invoicing = reg('stock.invoice.onshipping')
        invoicing_context = {
            'active_ids': picking_ids,
            'active_id': picking_ids[0],
            'active_model': 'stock.picking',
            }
        invoicing_id = invoicing.create(
            cr, uid, {'group': True}, context=invoicing_context
            )
        res = invoicing.create_invoice(
            cr, uid, [invoicing_id], context=invoicing_context)
        return res.items()[0][1]

    def test_00_picking_to_order(self):
        """
        Create two purchase orders with invoice method 'picking'.
        After delivery of the pickings, create a single invoice.
        Change the invoice method of one of the orders to 'order'
        and run through this order's workflow until completed.
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        po_pool = reg('purchase.order')
        po1_id = self.create_order('picking')
        po2_id = self.create_order('picking')

        # Confirm and receive the purchases
        self.wf_service.trg_validate(
            uid, 'purchase.order', po1_id, 'purchase_confirm', cr)
        self.wf_service.trg_validate(
            uid, 'purchase.order', po2_id, 'purchase_confirm', cr)
        po1, po2 = po_pool.browse(
            cr, uid, [po1_id, po2_id])
        self.wf_service.trg_validate(
            uid, 'stock.picking', po1.picking_ids[0].id, 'button_done', cr)
        self.wf_service.trg_validate(
            uid, 'stock.picking', po2.picking_ids[0].id, 'button_done', cr)
        self.assert_state(po1, 'approved')
        self.assert_state(po2, 'approved')
        for picking in po1.picking_ids[0], po2.picking_ids[0]:
            self.assertTrue(
                picking.state == 'done' and
                picking.invoice_state == '2binvoiced',
                'Picking is not ready for invoicing')

        invoice_id = self.create_invoice_from_pickings(
            [po1.picking_ids[0].id, po2.picking_ids[0].id])

        # Reset the first purchase order's invoice method
        po1.reset_invoice_method('order')
        po1.refresh()
        po2.refresh()

        # The original draft invoice has been removed
        # and the picking's invoice states have been updated
        # according to each order's invoice control
        self.assertFalse(
            reg('account.invoice').search(
                cr, uid, [('id', '=', invoice_id)]),
            'Obsolete invoice has not been removed after changing invoice '
            'method')
        self.assertTrue(
            po1.picking_ids[0].invoice_state == 'none',
            'Picking from order has not been set not to be invoiced')
        self.assertTrue(
            po2.picking_ids[0].invoice_state == '2binvoiced',
            'Picking from second order has not been reset to be invoiced')

        # A new invoice for the first order has been created through
        # the workflow. Confirm this invoice.
        self.assertTrue(
            len(po1.invoice_ids) == 1,
            'Unexpected number of invoices for first order '
            '(other than 1): %s' % (len(po1.invoice_ids)))
        self.wf_service.trg_validate(
            uid, 'account.invoice', po1.invoice_ids[0].id, 'invoice_open', cr)
        po1.refresh()
        self.assertTrue(
            po1.invoice_ids[0].state == 'open',
            'Did not succeed in confirming the generated invoice')

        self.pay_invoice(po1)
        self.assertTrue(
            po1.state == 'done',
            'Purchase order workflow did not complete after paying the '
            'invoice')

    def test_01_order_to_picking(self):
        """
        Create a purchase order with invoice method 'order'.
        After confirming the order, change the invoice method
        to 'picking' and run through this order's workflow until completed.
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        po_pool = reg('purchase.order')
        po_id = self.create_order('order')

        # Confirm and receive the purchases
        self.wf_service.trg_validate(
            uid, 'purchase.order', po_id, 'purchase_confirm', cr)
        po = po_pool.browse(cr, uid, po_id)
        self.assertTrue(
            len(po.invoice_ids) == 1,
            'Unexpected number of invoices for purchase order '
            '(other than 1): %s' % len(po.invoice_ids))

        invoice_id = po.invoice_ids[0].id

        # Reset the purchase order's invoice method
        po.reset_invoice_method('picking')
        po.refresh()

        # The original draft invoice has been removed
        # and the picking's invoice states have been updated
        # according to each order's invoice control
        self.assertFalse(
            reg('account.invoice').search(
                cr, uid, [('id', '=', invoice_id)]),
            'Obsolete invoice has not been removed after changing invoice '
            'method')

        # Check that the purchase order is not in an invoice exception
        # after unlinking the original invoice
        self.assert_state(po, 'approved')

        self.wf_service.trg_validate(
            uid, 'stock.picking', po.picking_ids[0].id, 'button_done', cr)
        self.assertTrue(
            po.picking_ids[0].state == 'done' and
            po.picking_ids[0].invoice_state == '2binvoiced',
            'Picking is not ready for invoicing')
        invoice_id = self.create_invoice_from_pickings([po.picking_ids[0].id])
        self.wf_service.trg_validate(
            uid, 'account.invoice', po.invoice_ids[0].id, 'invoice_open', cr)
        po.refresh()
        self.assertTrue(
            po.invoice_ids[0].state == 'open',
            'Did not succeed in confirming the generated invoice')
        self.assertTrue(
            po.state == 'done',
            'Purchase order workflow did not complete after paying the '
            'invoice when changing invoice method from order to picking')

    def test_02_lines_to_picking(self):
        """
        Create two orders set to 'manual', and invoice their lines together.
        Reset the first order's invoice method to 'picking'. Finish both
        orders' workflows.
        """
        reg, cr, uid, = self.registry, self.cr, self.uid
        po_pool = reg('purchase.order')
        po_id = self.create_order('manual')
        po2_id = self.create_order('manual')

        # Confirm and receive the purchases
        self.wf_service.trg_validate(
            uid, 'purchase.order', po_id, 'purchase_confirm', cr)
        self.wf_service.trg_validate(
            uid, 'purchase.order', po2_id, 'purchase_confirm', cr)
        po = po_pool.browse(cr, uid, po_id)
        po2 = po_pool.browse(cr, uid, po2_id)

        invoicing_context = {'active_ids': [
            line.id for line in po.order_line + po2.order_line]}
        reg('purchase.order.line_invoice').makeInvoices(
            cr, uid, False, invoicing_context)
        po.refresh()

        self.assertTrue(
            len(po.invoice_ids) == 1,
            'Unexpected number of invoices for purchase order '
            '(other than 1): %s' % len(po.invoice_ids))
        invoice_id = po.invoice_ids[0].id

        # Reset the purchase order's invoice method
        po.reset_invoice_method('picking')
        po.refresh()
        po2.refresh()

        # The original draft invoice has been removed
        # and the picking's invoice states have been updated
        # according to each order's invoice control
        self.assertFalse(
            reg('account.invoice').search(
                cr, uid, [('id', '=', invoice_id)]),
            'Obsolete invoice has not been removed after changing invoice '
            'method')

        # Check that the purchase order is not in an invoice exception
        # after unlinking the original invoice
        self.assert_state(po, 'approved')

        self.wf_service.trg_validate(
            uid, 'stock.picking', po.picking_ids[0].id, 'button_done', cr)
        self.assertTrue(
            po.picking_ids[0].state == 'done' and
            po.picking_ids[0].invoice_state == '2binvoiced',
            'Picking is not ready for invoicing')
        invoice_id = self.create_invoice_from_pickings([po.picking_ids[0].id])
        self.wf_service.trg_validate(
            uid, 'account.invoice', invoice_id, 'invoice_open', cr)

        po.refresh()
        self.assertTrue(
            po.invoice_ids[0].state == 'open',
            'Did not succeed in confirming the generated invoice')
        self.assertTrue(
            po.state == 'done',
            'Purchase order workflow did not complete after paying the '
            'invoice when changing invoice method from order to picking')

        # Recreate the invoice for the second order and finish
        # its workflow with the original 'manual' invoice control
        self.assertFalse(
            po2.order_line[0].invoiced,
            'Second order\'s line invoice state has not been reset')
        invoicing_context = {'active_ids': [
            line.id for line in po2.order_line]}
        reg('purchase.order.line_invoice').makeInvoices(
            cr, uid, False, invoicing_context)
        po2.refresh()
        self.wf_service.trg_validate(
            uid, 'stock.picking', po2.picking_ids[0].id, 'button_done', cr)
        self.wf_service.trg_validate(
            uid, 'account.invoice', po2.invoice_ids[0].id, 'invoice_open', cr)
        po2.refresh()
        self.assertTrue(
            po2.state == 'done',
            'Purchase order workflow did not complete after paying the '
            'invoice when changing invoice method from order to picking')
        self.assertTrue(
            po2.order_line[0].invoiced,
            'Second order\'s line is not set to invoiced')
