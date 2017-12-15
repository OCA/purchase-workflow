# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_additional_fields(self, invoice):
        if self.purchase_line_id:
            self.sequence = self.purchase_line_id.sequence
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)
