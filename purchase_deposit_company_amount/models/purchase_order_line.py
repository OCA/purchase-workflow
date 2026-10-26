# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
    )
    deposit_company_amount = fields.Monetary(
        string="Deposit Company-Currency Amount",
        compute="_compute_deposit_company_amount",
        currency_field="company_currency_id",
        help="Company-currency value actually booked by the posted deposit "
        "vendor bill(s) for this deposit line, and zero unless one of them "
        "carries a hand-entered Company Currency Amount. The final vendor bill "
        "pins its deposit-offset line to this value so the deposit account "
        "closes out at the amount that was really paid, whatever the exchange "
        "rate has done since.",
    )

    @api.depends(
        "is_deposit",
        "invoice_lines.balance",
        "invoice_lines.company_amount",
        "invoice_lines.quantity",
        "invoice_lines.parent_state",
    )
    def _compute_deposit_company_amount(self):
        for line in self:
            line.deposit_company_amount = 0.0
            if not line.is_deposit:
                continue
            booked_lines = line.invoice_lines.filtered(
                lambda l: l.quantity > 0
                and l.parent_state == "posted"
                and l.move_id.move_type in ("in_invoice", "in_refund")
            )
            if not booked_lines.filtered("company_amount"):
                continue
            line.deposit_company_amount = sum(booked_lines.mapped("balance"))
