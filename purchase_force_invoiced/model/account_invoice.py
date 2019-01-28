# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        purchase_order_line_model = self.env['purchase.order.line']
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line)
        if res.get('purchase_line_id', False):
            pol = purchase_order_line_model.browse(res['purchase_line_id'])
            if pol.order_id.force_invoiced:
                res['quantity'] = 0.0
        return res
