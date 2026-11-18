# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


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
        compute="_compute_percent",
        store=True,
        readonly=False,
        help="This percent will be used to calculate new quantity",
    )
    amount = fields.Float(
        digits="Product Price",
        compute="_compute_amount",
        inverse="_inverse_amount",
        help="This amount will be used to calculate the percent",
    )
    invoice_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="purchase_invoice_plan_id",
        string="Bill Lines",
        readonly=True,
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        relation="purchase_invoice_plan_invoice_rel",
        column1="plan_id",
        column2="move_id",
        string="Invoices",
        compute="_compute_invoice_ids",
        store=True,
    )
    amount_invoiced = fields.Float(
        compute="_compute_invoiced",
        store=True,
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

    @api.depends("invoiced", "amount_invoiced", "purchase_id.amount_untaxed")
    def _compute_percent(self):
        """Percent of an invoiced installment follows its invoiced amount"""
        for rec in self:
            amount_untaxed = rec.purchase_id.amount_untaxed
            if rec.invoiced and amount_untaxed:
                rec.percent = rec.amount_invoiced / amount_untaxed * 100

    @api.depends("percent", "invoiced", "amount_invoiced")
    def _compute_amount(self):
        for rec in self:
            amount_untaxed = rec.purchase_id._origin.amount_untaxed
            # With invoice already created, no recompute
            if rec.invoiced:
                rec.amount = rec.amount_invoiced
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

    @api.depends(
        "purchase_id.state",
        "purchase_id.invoice_plan_ids.invoiced",
        "purchase_id.invoice_plan_ids.installment",
    )
    def _compute_to_invoice(self):
        """If any invoice is in draft/open/paid do not allow to create inv
        Only the first installment not invoiced of each order is to_invoice
        """
        for order, plans in self.grouped("purchase_id").items():
            next_plan = plans.browse()
            if order.state == "purchase":
                next_plan = order._get_next_invoice_plan()
            for rec in plans:
                rec.to_invoice = rec == next_plan

    @api.depends("invoice_line_ids.move_id")
    def _compute_invoice_ids(self):
        for rec in self:
            rec.invoice_ids = rec.invoice_line_ids.move_id

    def _get_amount_invoice(self, invoices):
        """Hook function"""
        self.ensure_one()
        lines = self.invoice_line_ids.filtered(lambda ln: ln.move_id in invoices)
        return sum(lines.mapped("price_subtotal"))

    @api.depends(
        "invoice_ids.state",
        "invoice_ids.move_type",
        "invoice_line_ids.price_subtotal",
    )
    def _compute_invoiced(self):
        for rec in self:
            # A bill switched to refund (negative total) is not an installment
            invoiced = rec.invoice_ids.filtered(
                lambda inv: (
                    inv.move_type == "in_invoice" and inv.state in ("draft", "posted")
                )
            )
            rec.invoiced = bool(invoiced)
            rec.amount_invoiced = rec._get_amount_invoice(invoiced)

    @api.depends("installment", "purchase_id.invoice_plan_ids.installment")
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

    def _get_invoice_line_quantity(self, order_line, quantity):
        """Hook function: quantity of order_line to bill in this installment

        :param quantity: invoiceable quantity computed by the standard
        """
        self.ensure_one()
        if self.last:  # For last install, let the system do the calc.
            return quantity
        plan_qty = self._get_plan_qty(order_line, self.percent)
        # Not more than the standard, which is negative after a return
        if order_line.uom_id.compare(plan_qty, quantity) > 0:
            if self.env.context.get("invoice_plan_id") != self.id:
                # Bill not created by plan, do not bill more than the standard
                return quantity
            raise ValidationError(
                self.env._(
                    "Plan quantity: %(plan)s, exceed invoiceable quantity: %(qty)s"
                    "\nProduct should be delivered before invoice",
                    plan=plan_qty,
                    qty=quantity,
                )
            )
        return plan_qty

    def _get_invoiced_ratio(self):
        """Part of the purchase order untaxed amount billed by this installment,
        with the quantities billed by the standard flows"""
        self.ensure_one()
        order = self.purchase_id
        if not order.amount_untaxed:
            return self.percent / 100
        amount = 0.0
        for line in order.order_line.filtered(
            lambda ln: ln._is_invoice_plan_line() and ln.product_qty
        ):
            quantity = self._get_invoice_line_quantity(line, line.qty_to_invoice)
            amount += line.price_subtotal * quantity / line.product_qty
        return amount / order.amount_untaxed

    def _get_downpayment_line_quantity(self, order_line, quantity):
        """Hook function: quantity of the down payment order_line deducted
        by this installment, in proportion of the installment, as
        sale_invoice_plan does. The last installment deducts the remaining.

        :param quantity: deduction of the standard, all the remaining
            down payment (negative)
        """
        self.ensure_one()
        if self.last:
            return quantity
        down_payment_lines = order_line.invoice_lines.filtered(
            lambda ln: (
                ln.move_id.move_type == "in_invoice"
                and ln.parent_state != "cancel"
                and ln.quantity > 0
            )
        )
        down_payment_qty = sum(
            ln.product_uom_id._compute_quantity(ln.quantity, order_line.uom_id)
            if ln.product_uom_id and order_line.uom_id
            else ln.quantity
            for ln in down_payment_lines
        )
        # Not more than the remaining down payment
        return max(-down_payment_qty * self._get_invoiced_ratio(), quantity)

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = order_line.product_qty * (percent / 100)
        return plan_qty

    @api.model_create_multi
    def create(self, vals_list):
        plans = super().create(vals_list)
        plans._check_percent()
        return plans

    def write(self, vals):
        res = super().write(vals)
        if {"percent", "installment", "purchase_id"} & set(vals):
            self._check_percent()
        return res

    def _check_percent(self):
        """Check installments entered by the user. Not a constraint, as the
        percent recomputed from an invoiced amount may exceed the plan.
        Installments written from their order are checked by the order, once
        all of them are written."""
        if self.env.context.get("invoice_plan_check_by_order"):
            return
        self.purchase_id._check_ip_total_percent()
        self.purchase_id._check_invoice_plan()

    @api.ondelete(at_uninstall=False)
    def _unlink_except_no_edit(self):
        lines = self.filtered("no_edit")
        if lines:
            installments = [str(x) for x in lines.mapped("installment")]
            raise UserError(
                self.env._(
                    "Installment %s: already used and not allowed to delete.\n"
                    "Please discard changes.",
                    ", ".join(installments),
                )
            )

    @api.depends("purchase_id", "installment", "plan_date", "percent")
    def _compute_display_name(self):
        for rec in self:
            display_name = (
                f"{rec.purchase_id.name}, "
                f"Invoice Plan #{rec.installment}: {rec.plan_date} ({rec.percent}%)"
            )
            rec.display_name = display_name
