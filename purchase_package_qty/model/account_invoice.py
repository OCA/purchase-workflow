# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Package Quantity Module for Odoo
#    Copyright (C) 2016-Today Akretion (https://www.akretion.com)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                self.invoice_line_ids -= line
            else:
                line.price_policy = line.purchase_line_id.price_policy
                line.package_qty = line.purchase_line_id.package_qty
                line.product_qty_package = line.package_qty and\
                    line.quantity / line.package_qty or 0
        return res

    @api.multi
    def get_taxes_values(self):
        # We have to override the method in account module
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.price_policy == 'package':
                taxes = line.invoice_line_tax_ids.compute_all(
                    price_unit, self.currency_id, line.product_qty_package,
                    line.product_id, self.partner_id)['taxes']
            else:
                taxes = line.invoice_line_tax_ids.compute_all(
                    price_unit, self.currency_id, line.quantity,
                    line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and
                    line.account_analytic_id.id or False,
                    'account_id': self.type in (
                        'out_invoice', 'in_invoice') and
                    (tax['account_id'] or line.account_id.id) or
                    (tax['refund_account_id'] or line.account_id.id),
                    'base': tax['base'],
                }

                # If the taxes generate moves on the same financial account as
                # the invoice line, propagate the analytic account from the
                # invoice line to the tax line.
                # This is necessary in situations were (part of) the taxes
                # cannot be reclaimed, to ensure the tax move is allocated to
                # the proper analytic account.
                if not val.get('account_analytic_id') and\
                        line.account_analytic_id and\
                        val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = self.env['account.tax'].browse(tax['id']).\
                    get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped
