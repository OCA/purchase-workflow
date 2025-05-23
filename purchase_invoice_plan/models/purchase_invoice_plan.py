# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


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
    installment = fields.Integer()
    plan_date = fields.Date(
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
        digits="Purchase Invoice Plan Percent",
        help="This percent will be used to calculate new quantity",
    )
    amount = fields.Float(
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
    amount_invoiced = fields.Float(
        compute="_compute_invoiced",
        store=True,
        readonly=False,
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
    no_edit = fields.Boolean(
        compute="_compute_no_edit",
    )

    @api.depends("percent")
    def _compute_amount(self):
        for rec in self:
            amount_untaxed = rec.purchase_id._origin.amount_untaxed
            # With invoice already created, no recompute
            if rec.invoiced:
                rec.amount = rec.amount_invoiced
                rec.percent = rec.amount / amount_untaxed * 100
                continue
            # For last line, amount is the left over
            if rec.last:
                installments = rec.purchase_id.invoice_plan_ids.filtered(
                    lambda pln: pln.invoice_type == "installment"
                )
                prev_amount = sum((installments - rec).mapped("amount"))
                rec.amount = amount_untaxed - prev_amount
                continue
            rec.amount = rec.percent * amount_untaxed / 100

    @api.onchange("amount", "percent")
    def _inverse_amount(self):
        for rec in self:
            if rec.purchase_id.amount_untaxed != 0:
                if rec.last:
                    installments = rec.purchase_id.invoice_plan_ids.filtered(
                        lambda pln: pln.invoice_type == "installment"
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

    def _get_amount_invoice(self, invoices):
        """Hook function"""
        return sum(invoices.mapped("amount_untaxed"))

    @api.depends("invoice_ids.state")
    def _compute_invoiced(self):
        for rec in self:
            invoiced = rec.invoice_ids.filtered(
                lambda inv: inv.state in ("draft", "posted")
            )
            rec.invoiced = invoiced and True or False
            rec.amount_invoiced = rec._get_amount_invoice(invoiced[:1])

    def _compute_last(self):
        for rec in self:
            last = max(rec.purchase_id.invoice_plan_ids.mapped("installment"))
            rec.last = rec.installment == last

    def _no_edit(self):
        self.ensure_one()
        return self.invoiced

    def _compute_no_edit(self):
        for rec in self:
            rec.no_edit = rec._no_edit()

    def _compute_new_invoice_quantity(self, invoice_move):
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return
        percent = self.percent
        move = invoice_move.with_context(**{"check_move_validity": False})
        for line in move.invoice_line_ids:
            self._update_new_quantity(line, percent)

    def _update_new_quantity(self, line, percent):
        """Hook function"""
        plan_qty = self._get_plan_qty(line.purchase_line_id, percent)
        prec = line.purchase_line_id.product_uom.rounding
        if (
            float_compare(abs(plan_qty), abs(line.quantity), precision_rounding=prec)
            == 1
        ):
            raise ValidationError(
                self.env._(
                    "Plan quantity: %(plan)s, exceed invoiceable quantity: %(qty)s"
                    "\nProduct should be delivered before invoice"
                )
                % {"plan": plan_qty, "qty": line.quantity}
            )
        line.write({"quantity": plan_qty})

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = order_line.product_qty * (percent / 100)
        return plan_qty

    @api.ondelete(at_uninstall=False)
    def _unlink_except_no_edit(self):
        lines = self.filtered("no_edit")
        if lines:
            installments = [str(x) for x in lines.mapped("installment")]
            raise UserError(
                self.env._(
                    "Installment %s: already used and not allowed to delete.\n"
                    "Please discard changes."
                )
                % ", ".join(installments)
            )

    @api.depends("purchase_id", "installment", "plan_date", "percent")
    def _compute_display_name(self):
        for rec in self:
            display_name = (
                f"{rec.purchase_id.name}, "
                f"Invoice Plan #{rec.installment}: {rec.plan_date} ({rec.percent}%)"
            )
            rec.display_name = display_name
