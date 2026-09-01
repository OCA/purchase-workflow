# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_deposit = fields.Boolean(
        string="Is a Deposit Bill",
        compute="_compute_is_deposit",
        help="Technical field: this bill was raised by the Register Deposit "
        "wizard, i.e. it books a deposit rather than netting one off. It is "
        "the only kind of bill on which the company-currency amount can be "
        "entered by hand.",
    )
    allow_company_amount = fields.Boolean(
        compute="_compute_allow_company_amount",
        help="Technical field: the company-currency amount may be entered by "
        "hand on this bill's deposit line.",
    )

    @api.depends(
        "invoice_line_ids.purchase_line_id.is_deposit",
        "invoice_line_ids.quantity",
    )
    def _compute_is_deposit(self):
        for move in self:
            move.is_deposit = bool(
                move.invoice_line_ids.filtered(
                    lambda l: l.purchase_line_id.is_deposit and l.quantity > 0
                )
            )

    @api.depends("is_deposit", "currency_id", "company_currency_id")
    def _compute_allow_company_amount(self):
        for move in self:
            move.allow_company_amount = bool(
                move.is_deposit and move.currency_id != move.company_currency_id
            )

    @api.constrains("currency_id", "line_ids")
    def _check_company_amount_allowed(self):
        self.line_ids._check_company_amount_allowed()

    def _get_deposit_offset_lines(self):
        self.ensure_one()
        return self.line_ids.filtered(
            lambda l: l.display_type == "product"
            and l.purchase_line_id.is_deposit
            and l.quantity < 0
        )

    def _get_absorbed_targets(self, absorbing_lines, delta):
        self.ensure_one()
        company_currency = self.company_currency_id
        if company_currency.is_zero(delta) or not absorbing_lines:
            return {}
        weights = {
            line: abs(line._get_rate_based_balance()) for line in absorbing_lines
        }
        total_weight = sum(weights.values())
        if not total_weight:
            return {}
        targets = {}
        remaining = delta
        last_line = absorbing_lines[-1]
        for line in absorbing_lines:
            if line == last_line:
                # The last line takes the rounding remainder, so the shares add
                # back up to the delta exactly and the move stays balanced.
                share = company_currency.round(remaining)
            else:
                share = company_currency.round(delta * weights[line] / total_weight)
                remaining -= share
            targets[line] = company_currency.round(
                line._get_rate_based_balance() + share
            )
        return targets

    def _get_company_amount_targets(self):
        self.ensure_one()
        company_currency = self.company_currency_id
        if self.currency_id == company_currency:
            return {}
        product_lines = self.line_ids.filtered(lambda l: l.display_type == "product")
        if not product_lines.filtered(lambda l: l.purchase_line_id.is_deposit):
            return {}
        targets = {}
        for line in product_lines.filtered("company_amount"):
            sign = -1 if line.amount_currency < 0 else 1
            targets[line] = sign * abs(line.company_amount)
        offset_lines = self._get_deposit_offset_lines()
        for line in offset_lines:
            deposit_amount = line.purchase_line_id.deposit_company_amount
            if line in targets or company_currency.is_zero(deposit_amount):
                continue
            sign = -1 if line.amount_currency < 0 else 1
            targets[line] = sign * abs(deposit_amount)
        delta = sum(
            line._get_rate_based_balance() - targets[line]
            for line in offset_lines
            if line in targets
        )
        absorbing_lines = product_lines.filtered(
            lambda l: l.purchase_line_id and not l.purchase_line_id.is_deposit
        )
        # The goods absorb delta: it is acquisition cost, not an FX gain or loss.
        targets.update(self._get_absorbed_targets(absorbing_lines, delta))
        for line in product_lines:
            targets.setdefault(line, line._get_rate_based_balance())
        return targets

    def _rebalance_payment_term_lines(self):
        self.ensure_one()
        company_currency = self.company_currency_id
        term_lines = self.line_ids.filtered(lambda l: l.display_type == "payment_term")
        if not term_lines:
            return
        imbalance = company_currency.round(sum(self.line_ids.mapped("balance")))
        if company_currency.is_zero(imbalance):
            return
        weights = {line: abs(line.balance) for line in term_lines}
        total_weight = sum(weights.values())
        remaining = imbalance
        for idx, line in enumerate(term_lines):
            if idx < len(term_lines) - 1:
                if total_weight:
                    share = company_currency.round(
                        imbalance * weights[line] / total_weight
                    )
                else:
                    share = company_currency.round(imbalance / len(term_lines))
                remaining -= share
            else:
                share = company_currency.round(remaining)
            line.balance = company_currency.round(line.balance - share)

    def _apply_company_amount_overrides(self):
        for move in self:
            if move.is_sale_document() or move.state == "posted":
                continue
            company_currency = move.company_currency_id
            targets = move._get_company_amount_targets()
            if not targets:
                continue
            rewritten = overriding = False
            for line, target in targets.items():
                if not company_currency.is_zero(line.balance - target):
                    line.balance = target
                    rewritten = True
                if not company_currency.is_zero(
                    target - line._get_rate_based_balance()
                ):
                    overriding = True
            if rewritten or overriding:
                move._rebalance_payment_term_lines()
