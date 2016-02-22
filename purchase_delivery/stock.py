# -*- coding: utf-8 -*-
# © # © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from openerp import models


class stock_picking(models.Model):

    _inherit = 'stock.picking'

    def _invoice_create_line(
            self, cr, uid, moves, journal_id,
            inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_ids = super(stock_picking, self)._invoice_create_line(
            cr, uid, moves, journal_id, inv_type=inv_type, context=context)
        delivey_invoices = {}
        for move in moves:
            key = (move.picking_id.partner_id.id, move.picking_id.id)
            for invoice in move.purchase_line_id.order_id.invoice_ids:
                if invoice.id in invoice_ids:
                    if key not in delivey_invoices:
                        delivey_invoices[key] = invoice
        if delivey_invoices:
            for key, invoice in delivey_invoices.items():
                picking = self.browse(cr, uid, key[1], context=context)
                invoice_line = self._prepare_shipping_invoice_line(
                    cr, uid, picking, invoice, context=context)
                if invoice_line:
                    invoice_line_obj.create(cr, uid, invoice_line)
                    invoice_obj.button_compute(
                        cr, uid, [invoice.id], context=context,
                        set_total=(inv_type in ('out_invoice', 'out_refund')))
        return invoice_ids
