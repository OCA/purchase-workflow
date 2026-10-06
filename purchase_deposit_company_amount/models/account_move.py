# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


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

    def _get_pinned_offset_lines(self):
        self.ensure_one()
        return self._get_deposit_offset_lines().filtered(
            lambda l: not self.company_currency_id.is_zero(
                l.purchase_line_id.deposit_company_amount
            )
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
            target = company_currency.round(line._get_rate_based_balance() + share)
            if target * line.amount_currency < 0:
                # The ledger forbids a balance that runs against the foreign
                # currency amount, so absorb nothing and let action_post
                # explain the refusal rather than hitting a database error.
                return {}
            targets[line] = target
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
        offset_lines = self._get_pinned_offset_lines()
        for line in offset_lines:
            if line in targets:
                continue
            sign = -1 if line.amount_currency < 0 else 1
            targets[line] = sign * abs(line.purchase_line_id.deposit_company_amount)
        delta = sum(
            line._get_rate_based_balance() - targets[line] for line in offset_lines
        )
        # The goods absorb delta: it is acquisition cost, not an FX gain or loss.
        absorbing_lines = product_lines.filtered(
            lambda l: l.purchase_line_id and not l.purchase_line_id.is_deposit
        )
        absorbed = self._get_absorbed_targets(absorbing_lines, delta)
        if not absorbed and not company_currency.is_zero(delta):
            # Pinning the deposit with nothing to absorb the difference would
            # only push it onto the payable. Put every line back on the
            # standard conversion, undoing what an earlier sync may have
            # written, and let action_post refuse the bill.
            return {line: line._get_rate_based_balance() for line in product_lines}
        targets.update(absorbed)
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

    def _check_order_billed_in_full(self, offset_lines):
        """The whole deposit is relieved on the first bill that follows it, so
        only a bill carrying every unit of the order can share the difference
        over all of them. A partial one would load it onto the quantities it
        happens to carry, valuing them wrongly in stock."""
        self.ensure_one()
        billed = dict.fromkeys(
            offset_lines.purchase_line_id.order_id.order_line.filtered(
                lambda l: not l.is_deposit and not l.display_type
            ),
            0.0,
        )
        for line in self.line_ids.filtered(lambda l: l.display_type == "product"):
            order_line = line.purchase_line_id
            if order_line in billed:
                billed[order_line] += line.product_uom_id._compute_quantity(
                    line.quantity, order_line.product_uom
                )
        pending = [
            line
            for line, qty in billed.items()
            if float_compare(
                qty, line.product_qty, precision_rounding=line.product_uom.rounding
            )
            < 0
        ]
        if not pending:
            return
        raise UserError(
            _(
                "This bill carries the whole deposit of %(orders)s, so it must "
                "invoice the whole order too: otherwise the difference between "
                "the deposit as paid and the exchange rate is charged to the "
                "quantities on this bill alone, valuing them wrongly in stock. "
                "Clear '%(field)s' on the deposit bill to fall back to the "
                "standard exchange rate conversion.\n\n"
                "Missing from this bill: %(lines)s"
            )
            % {
                "orders": ", ".join(
                    offset_lines.purchase_line_id.order_id.mapped("name")
                ),
                "field": self.env["account.move.line"]._fields["company_amount"].string,
                "lines": ", ".join(
                    "%s (%s)"
                    % (line.product_id.display_name, line.product_qty - billed[line])
                    for line in pending
                ),
            }
        )

    def _check_deposit_pin_supported(self):
        for move in self:
            if move.move_type != "in_invoice":
                continue
            offset_lines = move._get_pinned_offset_lines()
            if not offset_lines:
                continue
            move._check_order_billed_in_full(offset_lines)

    def action_post(self):
        self._check_deposit_pin_supported()
        return super().action_post()
