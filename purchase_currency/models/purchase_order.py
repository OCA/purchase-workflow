# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    currency_id = fields.Many2one(default=lambda self: self._default_currency_id())

    def _default_currency_id(self):
        company = self.env.company
        return company.default_purchase_currency_id or company.currency_id

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        default_currency_id = self.env.company.default_purchase_currency_id.id
        if not default_currency_id:
            return super().onchange_partner_id()
        return super(
            PurchaseOrder, self.with_context(default_currency_id=default_currency_id)
        ).onchange_partner_id()
