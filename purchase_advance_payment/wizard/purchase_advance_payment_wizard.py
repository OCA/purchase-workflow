# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import _, api, exceptions, fields, models
from odoo.tools import float_compare


class AccountVoucherWizardPurchase(models.TransientModel):

    _name = "account.voucher.wizard.purchase"
    _description = "Account Voucher Wizard Purchase"

    order_id = fields.Many2one("purchase.order", required=True)
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=True,
        domain=[("type", "in", ("bank", "cash"))],
    )
    journal_currency_id = fields.Many2one(
        "res.currency",
        "Journal Currency",
        store=True,
        readonly=False,
        compute="_compute_get_journal_currency",
    )
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    amount_total = fields.Monetary("Amount total", readonly=True)
    amount_advance = fields.Monetary(
        "Amount advanced", required=True, currency_field="journal_currency_id"
    )
    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    currency_amount = fields.Monetary(
        "Curr. amount", readonly=True, currency_field="currency_id"
    )
    payment_ref = fields.Char("Ref.")

    @api.depends("journal_id")
    def _compute_get_journal_currency(self):
        for wzd in self:
            wzd.journal_currency_id = (
                wzd.journal_id.currency_id.id or self.env.user.company_id.currency_id.id
            )

    @api.constrains("amount_advance")
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be positive."))
        if self.env.context.get("active_id", False):
            self.onchange_date()
            if (
                float_compare(
                    self.currency_amount,
                    self.order_id.amount_residual,
                    precision_digits=2,
                )
                > 0
            ):
                raise exceptions.ValidationError(
                    _("Amount of advance is greater than residual amount on purchase")
                )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        purchase_ids = self.env.context.get("active_ids", [])
        if not purchase_ids:
            return res
        purchase_id = fields.first(purchase_ids)
        purchase = self.env["purchase.order"].browse(purchase_id)
        if "amount_total" in fields_list:
            res.update(
                {
                    "order_id": purchase.id,
                    "amount_total": purchase.amount_residual,
                    "currency_id": purchase.currency_id.id,
                }
            )

        return res

    @api.onchange("journal_id", "date", "amount_advance")
    def onchange_date(self):
        if self.journal_currency_id != self.currency_id:
            amount_advance = self.journal_currency_id._convert(
                self.amount_advance,
                self.currency_id,
                self.order_id.company_id,
                self.date or fields.Date.today(),
            )
        else:
            amount_advance = self.amount_advance
        self.currency_amount = amount_advance

    def _prepare_payment_vals(self, purchase):
        partner_id = purchase.partner_id.id
        return {
            "date": self.date,
            "amount": self.amount_advance,
            "payment_type": "outbound",
            "partner_type": "supplier",
            "ref": self.payment_ref or purchase.name,
            "journal_id": self.journal_id.id,
            "currency_id": self.journal_currency_id.id,
            "partner_id": partner_id,
            "payment_method_id": self.env.ref(
                "account.account_payment_method_manual_out"
            ).id,
        }

    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        self.ensure_one()
        payment_obj = self.env["account.payment"]
        purchase_obj = self.env["purchase.order"]

        purchase_ids = self.env.context.get("active_ids", [])
        if purchase_ids:
            purchase_id = fields.first(purchase_ids)
            purchase = purchase_obj.browse(purchase_id)
            payment_vals = self._prepare_payment_vals(purchase)
            payment = payment_obj.create(payment_vals)
            purchase.account_payment_ids |= payment
            payment.action_post()

        return {
            "type": "ir.actions.act_window_close",
        }
