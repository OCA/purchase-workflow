# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    account_payment_ids = fields.One2many(
        "account.payment", "purchase_id", string="Pay purchase advanced", readonly=True
    )
    amount_residual = fields.Float(
        "Residual amount",
        readonly=True,
        compute="_compute_purchase_advance_payment",
        store=True,
    )
    payment_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment move lines",
        compute="_compute_purchase_advance_payment",
        store=True,
    )
    advance_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        string="Advance Payment Status",
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
        compute="_compute_purchase_advance_payment",
    )

    @api.depends(
        "currency_id",
        "company_id",
        "amount_total",
        "account_payment_ids",
        "account_payment_ids.state",
        "account_payment_ids.move_id",
        "account_payment_ids.move_id.line_ids",
        "account_payment_ids.move_id.line_ids.date",
        "account_payment_ids.move_id.line_ids.debit",
        "account_payment_ids.move_id.line_ids.credit",
        "account_payment_ids.move_id.line_ids.currency_id",
        "account_payment_ids.move_id.line_ids.amount_currency",
        "order_line.invoice_lines.move_id",
        "order_line.invoice_lines.move_id.amount_total",
        "order_line.invoice_lines.move_id.amount_residual",
    )
    def _compute_purchase_advance_payment(self):
        for order in self:
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.internal_type == "payable"
                and x.parent_state == "posted"
            )
            advance_amount = 0.0
            for line in mls:
                line_currency = line.currency_id or line.company_id.currency_id
                line_amount = line.amount_currency if line.currency_id else line.balance
                if line_currency != order.currency_id:
                    advance_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )
                else:
                    advance_amount += line_amount
            # Consider payments in related invoices.
            invoice_not_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_not_paid_amount += inv.amount_total - inv.amount_residual
            amount_residual = (
                order.amount_total - advance_amount - invoice_not_paid_amount
            )
            payment_state = "not_paid"
            if mls or order.invoice_ids:
                has_due_amount = float_compare(
                    amount_residual, 0.0, precision_rounding=order.currency_id.rounding
                )
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"
            order.payment_line_ids = mls
            order.amount_residual = amount_residual
            order.advance_payment_status = payment_state
