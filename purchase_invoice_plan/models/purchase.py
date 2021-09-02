# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_plan_ids = fields.One2many(
        comodel_name="purchase.invoice.plan",
        inverse_name="purchase_id",
        string="Invoice Plan",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    use_invoice_plan = fields.Boolean(
        string="Use Invoice Plan",
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
                and len(rec.invoice_plan_ids.filtered(lambda l: not l.invoiced))
            )

    @api.constrains("state")
    def _check_invoice_plan(self):
        for rec in self:
            if rec.state != "draft":
                if rec.invoice_plan_ids.filtered(lambda l: not l.percent):
                    raise ValidationError(
                        _("Please fill percentage for all invoice plan lines")
                    )

    def button_confirm(self):
        if self.filtered(lambda r: r.use_invoice_plan and not r.invoice_plan_ids):
            raise UserError(_("Use Invoice Plan selected, but no plan created"))
        return super().button_confirm()

    def create_invoice_plan(
        self, num_installment, installment_date, interval, interval_type
    ):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        invoice_plans = []
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
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
        invoice_plan_id = self._context.get("invoice_plan_id")
        if invoice_plan_id:
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


class PurchaseInvoicePlan(models.Model):
    _name = "purchase.invoice.plan"
    _description = "Invoice Planning Detail"
    _order = "installment"

    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchases Order",
        index=True,
        readonly=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        related="purchase_id.partner_id",
        store=True,
        index=True,
    )
    state = fields.Selection(
        string="Status",
        related="purchase_id.state",
        store=True,
        index=True,
    )
    installment = fields.Integer(
        string="Installment",
    )
    plan_date = fields.Date(
        string="Plan Date",
        required=True,
    )
    invoice_type = fields.Selection(
        selection=[("installment", "Installment")],
        string="Type",
        required=True,
        default="installment",
    )
    last = fields.Boolean(
        string="Last Installment",
        compute="_compute_last",
        help="Last installment will create invoice use remaining amount",
    )
    percent = fields.Float(
        string="Percent",
        digits="Product Unit of Measure",
        help="This percent will be used to calculate new quantity",
    )
    amount = fields.Float(
        string="Amount",
        digits="Product Price",
        compute="_compute_amount",
        inverse="_inverse_amount",
        help="This amount will be used to calculate the percent",
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        relation="purchase_invoice_plan_invoice_rel",
        column1="plan_id",
        column2="move_id",
        string="Invoices",
        readonly=True,
    )
    to_invoice = fields.Boolean(
        string="Next Invoice",
        compute="_compute_to_invoice",
        help="If this line is ready to create new invoice",
        store=True,
    )
    invoiced = fields.Boolean(
        string="Invoice Created",
        compute="_compute_invoiced",
        help="If this line already invoiced",
        store=True,
    )

    @api.depends("percent")
    def _compute_amount(self):
        for rec in self:
            if rec.last:
                installments = rec.purchase_id.invoice_plan_ids.filtered(
                    lambda l: l.invoice_type == "installment"
                )
                prev_amount = sum((installments - rec).mapped("amount"))
                rec.amount = rec.purchase_id.amount_untaxed - prev_amount
                continue
            rec.amount = rec.percent * rec.purchase_id.amount_untaxed / 100

    @api.onchange("amount", "percent")
    def _inverse_amount(self):
        for rec in self:
            if rec.purchase_id.amount_untaxed != 0:
                if rec.last:
                    installments = rec.purchase_id.invoice_plan_ids.filtered(
                        lambda l: l.invoice_type == "installment"
                    )
                    prev_percent = sum((installments - rec).mapped("percent"))
                    rec.percent = 100 - prev_percent
                    continue
                rec.percent = rec.amount / rec.purchase_id.amount_untaxed * 100
                continue
            rec.percent = 0

    @api.depends("purchase_id.state", "purchase_id.invoice_plan_ids.invoiced")
    def _compute_to_invoice(self):
        """If any invoice is in draft/open/paid do not allow to create inv
        Only if previous to_invoice is False, it is eligible to_invoice
        """
        for rec in self:
            rec.to_invoice = False
        for rec in self.sorted("installment"):
            if rec.purchase_id.state != "purchase":
                continue
            if not rec.invoiced:
                rec.to_invoice = True
                break

    @api.depends("invoice_ids.state")
    def _compute_invoiced(self):
        for rec in self:
            invoiced = rec.invoice_ids.filtered(
                lambda l: l.state in ("draft", "posted")
            )
            rec.invoiced = invoiced and True or False

    def _compute_last(self):
        for rec in self:
            last = max(rec.purchase_id.invoice_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        move = invoice_move.with_context({"check_move_validity": False})
        for line in move.invoice_line_ids:
            self._update_new_quantity(line, percent)
        move._move_autocomplete_invoice_lines_values()  # recompute dr/cr

    def _update_new_quantity(self, line, percent):
        """ Hook function """
        plan_qty = self._get_plan_qty(line.purchase_line_id, percent)
        prec = line.purchase_line_id.product_uom.rounding
        if float_compare(abs(plan_qty), abs(line.quantity), prec) == 1:
            raise ValidationError(
                _(
                    "Plan quantity: %s, exceed invoiceable quantity: %s"
                    "\nProduct should be delivered before invoice"
                )
                % (plan_qty, line.quantity)
            )
        line.write({"quantity": plan_qty})

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = order_line.product_qty * (percent / 100)
        return plan_qty
