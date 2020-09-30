# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_shipping_id", "company_id")
    def _onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        fiscal_position = self.fiscal_position_id
        res = super()._onchange_partner_shipping_id()
        if fiscal_position and fiscal_position != self.fiscal_position_id:
            self.fiscal_position_id = fiscal_position
        return res

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        fiscal_position = self.fiscal_position_id
        res = super()._onchange_partner_id()
        if fiscal_position:
            self.fiscal_position_id = fiscal_position
        self._onchange_fiscal_position_allowed_journal()
        return res
