# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_additional_fields(self, invoice):
        if self.purchase_line_id:
            self.sequence = self.purchase_line_id.sequence
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)
