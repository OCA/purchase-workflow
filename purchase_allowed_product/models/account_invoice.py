# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    use_only_supplied_product = fields.Boolean(
        string="Use only allowed products",
        help="If checked, only the products provided by this supplier "
             "will be shown.")

    @api.onchange('partner_id')
    def partner_id_change(self):
        only_supp_prod = self.partner_id.use_only_supplied_product
        if not only_supp_prod:
            only_supp_prod = self.partner_id.commercial_partner_id.\
                use_only_supplied_product
        self.use_only_supplied_product = only_supp_prod
