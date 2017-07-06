# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def _compute_price(self):
        """Overwrite price subtotal computation if the partner has a
        supplier rounding method set to 'Round Net Price'"""
        invoice = self.invoice_id
        if invoice and invoice.type in ['in_invoice', 'in_refund'] and\
                invoice.partner_id.supplier_rounding_method\
                == 'round_net_price':
            price = round(
                self.price_unit * (1 - (self.discount or 0.0) / 100.0),
                self.env['decimal.precision'].precision_get('Account'))
            taxes = self.invoice_line_tax_id.compute_all(
                price, self.quantity, product=self.product_id,
                partner=invoice.partner_id)
            self.price_subtotal = taxes['total']
            self.price_subtotal = invoice.currency_id.round(
                self.price_subtotal)
        else:
            return super(AccountInvoiceLine, self)._compute_price()
