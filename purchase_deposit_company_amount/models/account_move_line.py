# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    company_amount = fields.Monetary(
        string="Company Currency Amount",
        currency_field="company_currency_id",
        help="Company-currency value you actually paid for this line. When "
        "set, the line's balance is forced to this amount instead of the "
        "standard amount_currency / exchange_rate conversion, while the "
        "foreign-currency amount stays untouched. Enter it unsigned -- the "
        "debit/credit direction follows the line's foreign-currency amount. "
        "Leave it empty to keep the standard conversion. Only available on "
        "the deposit line of a deposit bill raised in a foreign currency; "
        "every other line follows from it automatically.",
    )

    @api.constrains("company_amount", "move_id")
    def _check_company_amount_allowed(self):
        for line in self.filtered("company_amount"):
            if line.move_id.allow_company_amount:
                continue
            raise ValidationError(
                _(
                    "'%(field)s' can only be set on a deposit bill raised in a "
                    "foreign currency. On line '%(line)s' of '%(move)s' the "
                    "standard exchange-rate conversion applies; clear the "
                    "value to continue."
                )
                % {
                    "field": line._fields["company_amount"].string,
                    "line": line.name or line.product_id.display_name or "/",
                    "move": line.move_id.display_name,
                }
            )

    @contextmanager
    def _sync_invoice(self, container):
        with super()._sync_invoice(container):
            yield
        if self.env.context.get("skip_company_amount_sync"):
            return
        lines = container["records"].with_context(skip_company_amount_sync=True)
        lines.move_id._apply_company_amount_overrides()

    def _get_rate_based_balance(self):
        self.ensure_one()
        if not self.currency_rate:
            return self.balance
        return self.company_currency_id.round(self.amount_currency / self.currency_rate)

    def _get_gross_unit_price(self):
        res = super()._get_gross_unit_price()
        if float_is_zero(
            self.quantity, precision_rounding=self.product_uom_id.rounding
        ):
            return res
        if (
            self.currency_id == self.company_currency_id
            or not self.move_id._get_deposit_offset_lines()
        ):
            return res
        if self.company_currency_id.is_zero(
            self.balance - self._get_rate_based_balance()
        ):
            return res
        return self.balance / self.quantity * self.currency_rate
