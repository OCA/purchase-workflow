# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class SelectWorkAcceptanceInvoicePlanWizard(models.TransientModel):
    _name = "select.work.acceptance.invoice.plan.wizard"
    _description = "Select Work Acceptance Invoice Plan Wizard"

    active_installment_ids = fields.Many2many(
        comodel_name="purchase.invoice.plan",
        compute="_compute_active_installment_ids",
    )
    installment_id = fields.Many2one(
        comodel_name="purchase.invoice.plan",
        string="Invoice Plan",
        required=True,
        domain="[('id', 'in', active_installment_ids), ('installment', '>', 0)]",
        help="List only installment that has not been used in WA (draft, accepted)",
    )
    apply_method_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Base On",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "select.work.acceptance.invoice.plan.wizard"),
        ],
        help="Choose the method to find matcing product line for this installment",
    )
    order_id = fields.Many2one(
        comodel_name="purchase.order",
        default=lambda self: self.env.context.get("active_id"),
    )
    order_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="select_wa_invoice_plan_order_line_rel",
        column1="wizard_id",
        column2="order_line_id",
        string="Product Filter",
        domain="[('order_id', '=', order_id)]",
        compute="_compute_order_line_ids",
        store=True,
        readonly=False,
        help="List of product lines used to create WA. Blank means all",
    )
    wa_qty_line_ids = fields.One2many(
        comodel_name="select.work.acceptance.invoice.plan.qty",
        inverse_name="wizard_id",
        compute="_compute_wa_qty_line_ids",
        store=True,
        readonly=False,
    )
    valid_amount = fields.Boolean(
        compute="_compute_valid_amount",
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        order = self.env["purchase.order"].browse(
            self.env.context.get("active_ids", [])
        )
        not_installment = order.invoice_plan_ids.filtered_domain(
            [("invoice_type", "!=", "installment")]
        )
        negative_qty = order.order_line.filtered(lambda l: l.product_qty <= 0)
        if not_installment and not negative_qty:
            raise UserError(_("Please register deposit first."))
        return res

    @api.depends("installment_id")
    def _compute_active_installment_ids(self):
        self.ensure_one()
        purchase = self.env["purchase.order"].browse(
            self.env.context.get("active_ids", [])
        )
        installment_ids = (
            purchase.wa_ids.filtered(lambda l: l.state != "cancel")
            .mapped("installment_id")
            .ids
        )
        self.active_installment_ids = self.env["purchase.invoice.plan"].search(
            [
                ("purchase_id", "=", purchase.id),
                ("id", "not in", installment_ids),
                ("installment", ">", 0),
            ]
        )

    @api.depends("installment_id", "apply_method_id")
    def _compute_order_line_ids(self):
        self.ensure_one()
        self.order_line_ids = False
        if self.installment_id and self.apply_method_id:
            ctx = {
                "installment_id": self.installment_id.id,
                "purchase_id": self.env.context.get("active_id"),
            }
            order_line_ids = self.apply_method_id.with_context(ctx).run()
            if not order_line_ids:
                raise UserError(_("No product line with matched amount!"))
            self.order_line_ids = order_line_ids  # [1,2,3,4]

    @api.depends("order_line_ids")
    def _compute_wa_qty_line_ids(self):
        Decimal = self.env["decimal.precision"]
        prec = Decimal.precision_get("Product Unit of Measure")
        for rec in self:
            rec.wa_qty_line_ids = False
            expect_amount = rec.installment_id.amount
            order_lines = rec.order_line_ids
            lines_amount = sum(order_lines.mapped("price_subtotal"))
            order = order_lines[:1].order_id
            all_lines_amount = sum(order.order_line.mapped("price_subtotal"))
            if rec.order_line_ids and not lines_amount:
                raise UserError(_("Total purchase amount must not be zero!"))
            for order_line in rec.order_line_ids:
                ratio = expect_amount / lines_amount
                ratio_all = expect_amount / all_lines_amount
                quantity = float_round(order_line.product_qty * ratio, prec)
                if not quantity:  # good for deposit case
                    quantity = -ratio_all
                if float_compare(quantity, order_line.qty_to_accept, 2) == 1:
                    quantity = order_line.qty_to_accept
                    amount = quantity * order_line.price_unit
                    expect_amount -= amount
                    order_lines -= order_line
                    lines_amount = sum(order_lines.mapped("price_subtotal"))
                line = self.env["select.work.acceptance.invoice.plan.qty"].new(
                    {"order_line_id": order_line._origin.id, "quantity": quantity}
                )
                rec.wa_qty_line_ids += line

    @api.depends("wa_qty_line_ids")
    def _compute_valid_amount(self):
        for rec in self:
            wa_amount = sum(rec.wa_qty_line_ids.mapped("amount"))
            installment = rec.installment_id.amount
            rec.valid_amount = float_compare(wa_amount, installment, 2) == 0

    @api.onchange("installment_id")
    def _onchange_installment_id(self):
        if not self.installment_id:
            return
        min_installment = min(self.active_installment_ids.mapped("installment"))
        if self.installment_id.installment > min_installment:
            return {
                "warning": {
                    "title": _("Installment Warning:"),
                    "message": _(
                        "The 1st installment is 'Invoice Plan %s' "
                        "but you are choosing 'Invoice Plan %s'"
                    )
                    % (min_installment, self.installment_id.installment),
                }
            }

    def button_create_wa(self):
        purchase = self.env["purchase.order"].browse(self.env.context.get("active_id"))
        if self.installment_id not in self.active_installment_ids:
            raise UserError(
                _(
                    "Installment {} is already used by other WA.".format(
                        self.installment_id.installment
                    )
                )
            )
        res = purchase.with_context(
            installment_id=self.installment_id.id,
            wa_qty_line_ids=self.wa_qty_line_ids.ids,
        ).action_view_wa()
        res["context"]["default_installment_id"] = self.installment_id.id
        return res


class ComputeWorkAcceptanceInvoicePlan(models.TransientModel):
    _name = "select.work.acceptance.invoice.plan.qty"
    _description = "Compute quantity of each WA lines, according to product lines"

    wizard_id = fields.Many2one(
        comodel_name="select.work.acceptance.invoice.plan.wizard",
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="wizard_id.order_id.currency_id",
    )
    order_id = fields.Many2one(
        related="wizard_id.order_id",
    )
    order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Product Line",
        required=True,
        index=True,
        domain="[('order_id', '=', order_id)]",
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        related="order_line_id.account_analytic_id",
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        related="order_line_id.analytic_tag_ids",
    )
    qty_not_accepted = fields.Float(
        string="Not Accepted",
        related="order_line_id.qty_to_accept",
        digits="Product Unit of Measure",
    )
    quantity = fields.Float(
        string="To Accept",
        digits="Product Unit of Measure",
    )
    amount = fields.Monetary(
        string="Amount",
        compute="_compute_amount",
        inverse="_inverse_amount",
    )
    _sql_constraints = [
        (
            "order_line_unique",
            "unique(wizard_id, order_line_id)",
            "You are selecting same product line more than one.",
        )
    ]

    @api.depends("quantity")
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.quantity * rec.order_line_id.price_unit

    @api.onchange("amount")
    def _inverse_amount(self):
        for rec in self:
            rec.quantity = rec.amount / rec.order_line_id.price_unit
