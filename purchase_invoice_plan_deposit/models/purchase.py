# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    need_advance = fields.Boolean(
        compute="_compute_need_advance",
        help="True if use 1st deposit invoice plan, but no deposit yet",
    )

    @api.constrains("invoice_plan_ids")
    def _check_invoice_plan_ids(self):
        for rec in self:
            for plan in rec.invoice_plan_ids:
                if plan.invoice_type == "advance" and plan.installment != 0:
                    raise UserError(_("Only installment 0 can be of type 'Deposit'"))

    def _compute_ip_invoice_plan(self):
        """With case advance in place, do overwrite"""
        for rec in self:
            has_invoice_plan = rec.use_invoice_plan and rec.invoice_plan_ids
            to_invoice = rec.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            if rec.state == "purchase" and has_invoice_plan and to_invoice:
                if rec.invoice_status == "to invoice" or (
                    rec.invoice_status == "no"
                    and "advance" in to_invoice.mapped("invoice_type")
                ):
                    rec.ip_invoice_plan = True
                    continue
            rec.ip_invoice_plan = False

    def create_invoice_plan(
        self, num_installment, installment_date, interval, interval_type
    ):
        advance = self.env.context.get("advance")
        advance_percent = self.env.context.get("advance_percent")
        advance_date = installment_date
        if advance:  # installment_date will be after advance_date
            installment_date = self._next_date(advance_date, interval, interval_type)
        # Call super to create non-advance installments
        res = super().create_invoice_plan(
            num_installment, installment_date, interval, interval_type
        )
        # Advance
        if advance:
            vals = {
                "installment": 0,
                "plan_date": advance_date,
                "invoice_type": "advance",
                "percent": advance_percent,
            }
            self.write({"invoice_plan_ids": [(0, 0, vals)]})
        return res

    def _compute_need_advance(self):
        for order in self:
            advance = order.invoice_plan_ids.filtered_domain(
                [("invoice_type", "=", "advance")]
            )
            deposit = order.order_line.filtered("is_deposit")
            order.need_advance = advance and not deposit

    def action_create_invoice(self):
        """If there is deposit installment, and no invoice is_deposit yet.
        Give user a warning.
        """
        if self.filtered("need_advance"):
            raise UserError(
                _("Invoice plan requires deposit, please register deposit first.")
            )
        return super().action_create_invoice()


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"

    invoice_type = fields.Selection(
        selection_add=[("advance", "Deposit")],
        ondelete={"advance": "cascade"},
    )

    def _update_new_quantity(self, line, percent):
        if line.purchase_line_id.is_deposit:  # based on 1 unit
            line.write({"quantity": -percent / 100})
            return
        super()._update_new_quantity(line, percent)

    def _get_amount_invoice(self, invoices):
        """Override _get_amount_invoice"""
        lines = invoices.mapped("invoice_line_ids").filtered(
            lambda l: not l.purchase_line_id.is_deposit
        )
        return sum(lines.mapped("price_subtotal"))
