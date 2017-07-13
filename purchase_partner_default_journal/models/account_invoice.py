# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # addons/account/models/account_invoice line #445
    @api.multi
    def _onchange_partner_id(self):
        result = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.type == 'in_invoice':
            # in case of an empty onchange value key is not there
            self.journal_id = self.partner_id.default_purchase_journal_id.id
        return result
