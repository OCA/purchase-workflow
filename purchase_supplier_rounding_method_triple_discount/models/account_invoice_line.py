# coding: utf-8
from openerp import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def _compute_price(self):
        invoice = self.invoice_id
        price = self.price_unit *\
            (1 - (self.discount or 0.0) / 100.0) *\
            (1 - (self.discount2 or 0.0) / 100.0) *\
            (1 - (self.discount3 or 0.0) / 100.0)

        if invoice and invoice.type in ['in_invoice', 'in_refund'] and\
                invoice.partner_id.supplier_rounding_method\
                == 'round_net_price':
            price = round(
                self.price_unit * (1 - (self.discount or 0.0) / 100.0),
                self.env['decimal.precision'].precision_get('Account'))

        taxes = self.invoice_line_tax_id.compute_all(
            price, self.quantity, product=self.product_id,
            partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if invoice:
            self.price_subtotal = invoice.currency_id.round(
                self.price_subtotal)
