# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('state', 'partner_id', 'invoice_line_ids')
    def _onchange_allowed_purchase_ids(self):
        """
        The purpose of the method is to define a domain for the available
        purchase orders.
        """
        result = super(AccountInvoice, self)._onchange_allowed_purchase_ids()
        result['domain']['purchase_id'] += [
            ('state', 'not in', ['done', 'cancel'])]
        return result

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id
        if self.purchase_id.state in ['done', 'cancel']:
            self.purchase_id = False
            return {}
        super(AccountInvoice, self).purchase_order_change()
