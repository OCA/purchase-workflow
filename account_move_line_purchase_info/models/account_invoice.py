# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        if line.purchase_line_id and res:
            res['purchase_line_id'] = line.purchase_line_id.id
        return res


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if line.get('purchase_line_id', False):
            res['purchase_line_id'] = line.get('purchase_line_id')
        return res
