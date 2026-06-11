# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, api, fields, models
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
                    raise UserError(
                        self.env._("Only installment 0 can be of type 'Deposit'")
                    )

    def _compute_ip_invoice_plan(self):
        """With case advance in place, do overwrite"""
        for rec in self:
            has_invoice_plan = rec.use_invoice_plan and rec.invoice_plan_ids
            to_invoice = rec.invoice_plan_ids.filtered(lambda pln: not pln.invoiced)
            if rec.state in ["purchase", "done"] and has_invoice_plan and to_invoice:
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
        advance_number = self.env.context.get("num_advance", 1)
        advance_date = installment_date
        if advance:  # installment_date will be after advance_date
            installment_date = self._next_date(advance_date, interval, interval_type)
        # Call super to create non-advance installments
        res = super().create_invoice_plan(
            num_installment, installment_date, interval, interval_type
        )
        # Create advance following advance number
        if advance:
            plan_deposit = [
                Command.create(
                    {
                        "installment": 0,
                        "plan_date": advance_date,
                        "invoice_type": "advance",
                        "percent": advance_percent,
                    }
                )
                for _num in range(advance_number)
            ]
            self.write({"invoice_plan_ids": plan_deposit})
        return res

    @api.depends("invoice_plan_ids.invoice_type", "invoice_plan_ids.advance_created")
    def _compute_need_advance(self):
        for order in self:
            advance = order.invoice_plan_ids.filtered_domain(
                [
                    ("invoice_type", "=", "advance"),
                    ("advance_created", "=", False),
                ]
            )
            order.need_advance = bool(advance)

    def action_create_invoice(self):
        """If there is deposit installment, and no invoice is_deposit yet.
        Give user a warning.
        """
        if (
            self.use_invoice_plan
            and self.env.context.get("advance_deduct_option")
            and not self.env.context.get("invoice_plan_id")
        ):
            return (
                self.env["purchase.make.planned.invoice"]
                .with_context(
                    advance_deduct_option=self.env.context.get("advance_deduct_option"),
                )
                .create({})
                .create_invoices_by_plan()
            )

        if self.filtered("need_advance"):
            raise UserError(
                self.env._(
                    "Invoice plan requires deposit, please register deposit first."
                )
            )
        return super().action_create_invoice()


class PurchaseInvoicePlan(models.Model):
    _inherit = "purchase.invoice.plan"
    _order = "installment, plan_date, id"

    invoice_type = fields.Selection(
        selection_add=[("advance", "Deposit")],
        ondelete={"advance": "cascade"},
    )
    advance_created = fields.Boolean()

    def _compute_to_invoice(self):
        for rec in self:
            rec.to_invoice = False

        advance_sorted = sorted(
            self.filtered(lambda pln: pln.invoice_type == "advance"),
            key=lambda pln: (
                pln.plan_date or "",
                pln.id if isinstance(pln.id, int) else 0,
            ),
        )
        regular_sorted = list(
            self.filtered(lambda pln: pln.invoice_type != "advance").sorted(
                "installment"
            )
        )
        for rec in advance_sorted + regular_sorted:
            if rec.purchase_id.state != "purchase":
                continue
            if not rec.invoiced:
                rec.to_invoice = True
                break

    def _update_new_quantity(self, line, percent):
        if line.purchase_line_id.is_deposit:  # based on 1 unit
            line.write({"quantity": -percent / 100})
            return
        super()._update_new_quantity(line, percent)

    def _get_amount_invoice(self, invoices):
        if self.invoice_type == "advance":
            return super()._get_amount_invoice(invoices)
        lines = invoices.mapped("invoice_line_ids").filtered(
            lambda line: not line.purchase_line_id.is_deposit
        )
        return sum(lines.mapped("price_subtotal"))
