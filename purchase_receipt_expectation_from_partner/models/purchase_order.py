# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("partner_id")
    def _onchange_partner_receipt_expectation(self):
        exp = self.partner_id.receipt_expectation
        if exp:
            self.receipt_expectation = exp
