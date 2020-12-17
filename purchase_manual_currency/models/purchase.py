# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    manual_currency = fields.Boolean()
    is_manual = fields.Boolean(compute="_compute_currency")
    custom_rate = fields.Float(
        digits="Purchase Currency",
        tracking=True,
        help="Set new currency rate to apply on the invoice\n."
        "This rate will be taken in order to convert amounts between the "
        "currency on the purchase order and last currency",
    )

    @api.depends("currency_id")
    def _compute_currency(self):
        for rec in self:
            rec.is_manual = rec.currency_id != rec.company_id.currency_id

    @api.onchange("currency_id", "date_order")
    def _onchange_currency_change_rate(self):
        today = fields.Date.today()
        main_currency = self.env.company.currency_id
        ctx = {"company_id": self.company_id.id, "date": self.date_order or today}
        self.custom_rate = main_currency.with_context(**ctx)._get_conversion_rate(
            main_currency, self.currency_id, self.company_id, self.date_order or today
        )

    def action_refresh_currency(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("Rate currency can refresh state draft only."))
        self._onchange_currency_change_rate()
        return True
