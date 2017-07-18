# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        vals = super(AccountInvoice,
                     self)._prepare_invoice_line_from_po_line(line)
        vals['discount2'] = line.discount2
        vals['discount3'] = line.discount3
        return vals
