# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp import netsvc


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    def reset_invoice_method_wizard(self, cr, uid, ids, context=None):
        wizard_id = self.pool['purchase.reset.invoice_method'].create(
            cr, uid, {'order_id': ids[0]}, context=context)
        return {
            'name': _('Reset invoice method'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.reset.invoice_method',
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': wizard_id,
        }

    def reset_invoice_method(
            self, cr, uid, ids, new_invoice_method, context=None):
        """
        Reset invoicing method of a purchase order. Clean up any draft
        invoices, reset picking invoice state and rest the invoicing
        path of the workflow. The affected invoices may be composed from
        other orders as well. If these invoices were derived from
        pickings, we need to reset the invoice state of these pickings as
        well.

        This will fail if any of the draft invoices has already been
        confirmed, as OpenERP does not allow unlinking these.
        """

        if len(ids) > 1:
            raise orm.except_orm(
                _('Error'),
                _('Please convert a single order at once.'))

        wf_service = netsvc.LocalService("workflow")
        order = self.browse(cr, uid, ids[0], context=context)
        old_invoice_method = order.invoice_method
        if old_invoice_method == new_invoice_method:
            raise orm.except_orm(
                _('Error'),
                _('The new invoice method is the same as the old.'))

        if order.invoice_ids:
            for invoice in order.invoice_ids:
                if invoice.state != 'draft':
                    raise orm.except_orm(
                        _('Error'),
                        _('This order has an invoice which is not in draft '
                          'state. Cannot reset the invoice method'))

                if old_invoice_method != 'picking':
                    continue

                # Track pickings and reset invoice state of foreign
                # pickings
                for inv_line in invoice.invoice_line:
                    if not inv_line.invoiced_stock_move_id:
                        raise orm.except_orm(
                            _('Error'),
                            _('This order has an old invoice created from a '
                              'picking, but without the picking reference '
                              'registered.'))
                    picking = inv_line.invoiced_stock_move_id.picking_id
                    if (picking.invoice_state == 'invoiced' and
                            picking not in order.picking_ids):
                        picking.write({'invoice_state': '2binvoiced'})
                        picking.refresh()

            # Reset invoice state of purchase lines
            order_line_ids = self.pool['purchase.order.line'].search(
                cr, uid, [
                    ('invoice_lines.invoice_id', 'in',
                     [inv.id for inv in order.invoice_ids])],
                context=context)
            self.pool['purchase.order.line'].write(
                cr, uid, order_line_ids,
                {'invoiced': False}, context=context)

            for invoice in order.invoice_ids:
                wf_service.trg_validate(
                    uid, 'account.invoice', invoice.id,
                    'invoice_cancel', cr)
                self.pool['account.invoice'].unlink(
                    cr, uid, [invoice.id],
                    context=context)

        if order.picking_ids:
            # Reset this order's pickings invoice state
            state = '2binvoiced' if new_invoice_method == 'picking' else 'none'
            self.pool['stock.picking'].write(
                cr, uid,
                [pick.id for pick in order.picking_ids],
                {'invoice_state': state}, context=context)

        order.write({'invoice_method': new_invoice_method})

        wf_service.trg_validate(
            uid, 'purchase.order', order.id,
            'reset_invoice_method_order', cr)
        return True
