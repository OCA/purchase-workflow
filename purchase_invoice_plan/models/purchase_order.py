# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_plan_ids = fields.One2many(
        comodel_name="purchase.invoice.plan",
        inverse_name="purchase_id",
        string="Invoice Plan",
        copy=False,
    )
    use_invoice_plan = fields.Boolean(
        default=False,
        copy=False,
    )
    ip_invoice_plan = fields.Boolean(
        string="Invoice Plan In Process",
        compute="_compute_ip_invoice_plan",
        help="At least one invoice plan line pending to create invoice",
    )
    ip_total_percent = fields.Float(
        compute="_compute_ip_total",
        string="Percent",
    )
    ip_total_amount = fields.Monetary(
        compute="_compute_ip_total",
        string="Total Amount",
    )

    @api.depends("invoice_plan_ids")
    def _compute_ip_total(self):
        for rec in self:
            installments = rec.invoice_plan_ids.filtered("installment")
            rec.ip_total_percent = sum(installments.mapped("percent"))
            rec.ip_total_amount = sum(installments.mapped("amount"))

    def _compute_ip_invoice_plan(self):
        for rec in self:
            rec.ip_invoice_plan = (
                rec.use_invoice_plan
                and rec.invoice_plan_ids
                and len(rec.invoice_plan_ids.filtered(lambda pln: not pln.invoiced))
            )

    @api.constrains("invoice_plan_ids")
    def _check_ip_total_percent(self):
        for rec in self:
            installments = rec.invoice_plan_ids.filtered("installment")
            ip_total_percent = sum(installments.mapped("percent"))
            if float_round(ip_total_percent, 0) > 100:
                raise UserError(
                    self.env._("Invoice plan total percentage must not exceed 100%")
                )

    @api.constrains("state")
    def _check_invoice_plan(self):
        for rec in self:
            if rec.state != "draft":
                if rec.invoice_plan_ids.filtered(lambda pln: not pln.percent):
                    raise ValidationError(
                        self.env._("Please fill percentage for all invoice plan lines")
                    )

    def button_confirm(self):
        if self.filtered(lambda r: r.use_invoice_plan and not r.invoice_plan_ids):
            raise UserError(
                self.env._("Use Invoice Plan selected, but no plan created")
            )
        return super().button_confirm()

    def create_invoice_plan(
        self, num_installment, installment_date, interval, interval_type
    ):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        invoice_plans = []
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Purchase Invoice Plan Percent")
        percent = float_round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment - 1))
        for i in range(num_installment):
            this_installment = i + 1
            if num_installment == this_installment:
                percent = percent_last
            vals = {
                "installment": this_installment,
                "plan_date": installment_date,
                "invoice_type": "installment",
                "percent": percent,
            }
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(
                installment_date, interval, interval_type
            )
        self.write({"invoice_plan_ids": invoice_plans})
        return True

    def remove_invoice_plan(self):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == "month":
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == "year":
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    def action_view_invoice(self, invoices=False):
        invoice_plan_id = self.env.context.get("invoice_plan_id")
        if invoice_plan_id and invoices:
            plan = self.env["purchase.invoice.plan"].browse(invoice_plan_id)
            for invoice in invoices:
                plan._compute_new_invoice_quantity(invoice)
                invoice.write(
                    {
                        "date": plan.plan_date,
                        "invoice_date": plan.plan_date,
                    }
                )
                plan.invoice_ids += invoice
        return super().action_view_invoice(invoices=invoices)
