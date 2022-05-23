# Copyright (C) 2018 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class BlanketOrder(models.Model):
    _name = "purchase.blanket.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Blanket Order"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def _default_company(self):
        return self.env.user.company_id

    @api.depends("line_ids.price_total")
    def _compute_amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    name = fields.Char(default="Draft", readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        readonly=True,
        track_visibility="always",
        states={"draft": [("readonly", False)]},
    )
    line_ids = fields.One2many(
        "purchase.blanket.order.line",
        "order_id",
        string="Order lines",
        track_visibility="always",
        copy=True,
    )
    line_count = fields.Integer(
        string="Purchase Blanket Order Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product", related="line_ids.product_id", string="Product",
    )
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.user.company_id.currency_id.id,
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Payment Terms",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    confirmed = fields.Boolean(copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("done", "Done"),
            ("expired", "Expired"),
        ],
        compute="_compute_state",
        store=True,
        copy=False,
        track_visibility="always",
    )
    validity_date = fields.Date(
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="always",
        help="Date until which the blanket order will be valid, after this "
        "date the blanket order will be marked as expired",
    )
    date_start = fields.Datetime(
        readonly=True,
        required=True,
        string="Start Date",
        default=fields.Datetime.now,
        states={"draft": [("readonly", False)]},
        help="Blanket Order starting date.",
    )
    note = fields.Text(readonly=True, states={"draft": [("readonly", False)]})
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda self: self.env.uid,
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=_default_company,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    purchase_count = fields.Integer(compute="_compute_purchase_count")

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position", string="Fiscal Position"
    )

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_all",
        track_visibility="always",
    )
    amount_tax = fields.Monetary(
        string="Taxes", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )

    # Fields use to filter in tree view
    original_uom_qty = fields.Float(
        string="Original quantity",
        compute="_compute_uom_qty",
        search="_search_original_uom_qty",
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_uom_qty",
        search="_search_ordered_uom_qty",
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_uom_qty",
        search="_search_invoiced_uom_qty",
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_uom_qty",
        search="_search_remaining_uom_qty",
    )
    received_uom_qty = fields.Float(
        string="Received quantity",
        compute="_compute_uom_qty",
        search="_search_received_uom_qty",
    )

    def _get_purchase_orders(self):
        return self.mapped("line_ids.purchase_lines.order_id")

    @api.depends("line_ids")
    def _compute_line_count(self):
        self.line_count = len(self.mapped("line_ids"))

    def _compute_purchase_count(self):
        for blanket_order in self:
            blanket_order.purchase_count = len(blanket_order._get_purchase_orders())

    @api.depends(
        "line_ids.remaining_uom_qty", "validity_date", "confirmed",
    )
    def _compute_state(self):
        today = fields.Date.today()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if not order.confirmed:
                order.state = "draft"
            elif order.validity_date <= today:
                order.state = "expired"
            elif float_is_zero(
                sum(order.line_ids.mapped("remaining_uom_qty")),
                precision_digits=precision,
            ):
                order.state = "done"
            else:
                order.state = "open"

    def _compute_uom_qty(self):
        for bo in self:
            bo.original_uom_qty = sum(bo.mapped("line_ids.original_uom_qty"))
            bo.ordered_uom_qty = sum(bo.mapped("line_ids.ordered_uom_qty"))
            bo.invoiced_uom_qty = sum(bo.mapped("line_ids.invoiced_uom_qty"))
            bo.received_uom_qty = sum(bo.mapped("line_ids.received_uom_qty"))
            bo.remaining_uom_qty = sum(bo.mapped("line_ids.remaining_uom_qty"))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Payment term
        """
        if not self.partner_id:
            self.payment_term_id = False
            self.fiscal_position_id = False
            return

        self.payment_term_id = (
            self.partner_id.property_supplier_payment_term_id
            and self.partner_id.property_supplier_payment_term_id.id
            or False
        )

        self.fiscal_position_id = (
            self.env["account.fiscal.position"]
            .with_context(company_id=self.company_id.id)
            .get_fiscal_position(self.partner_id.id)
        )

        self.currency_id = (
            self.partner_id.property_purchase_currency_id.id
            or self.env.user.company_id.currency_id.id
        )

        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id.id

    def unlink(self):
        for order in self:
            if order.state not in ("draft", "cancel"):
                raise UserError(
                    _(
                        "You can not delete an open blanket order! "
                        "Try to cancel it before."
                    )
                )
        return super().unlink()

    def copy_data(self, default=None):
        if default is None:
            default = {}
        default.update(self.default_get(["name", "confirmed"]))
        return super().copy_data(default)

    def _validate(self):
        try:
            today = fields.Date.today()
            for order in self:
                assert order.validity_date, _("Validity date is mandatory")
                assert order.validity_date > today, _(
                    "Validity date must be in the future"
                )
                assert order.partner_id, _("Partner is mandatory")
                assert len(order.line_ids) > 0, _("Must have some lines")
                order.line_ids._validate()
        except AssertionError as e:
            raise UserError(e)

    def set_to_draft(self):
        for order in self:
            order.write({"state": "draft"})
        return True

    def action_confirm(self):
        self._validate()
        for order in self:
            sequence_obj = self.env["ir.sequence"]
            if order.company_id:
                sequence_obj = sequence_obj.with_context(
                    force_company=order.company_id.id
                )
            name = sequence_obj.next_by_code("purchase.blanket.order")
            order.write({"confirmed": True, "name": name})
        return True

    def action_cancel(self):
        for order in self:
            if order.purchase_count > 0:
                for po in order._get_purchase_orders():
                    if po.state not in ("cancel"):
                        raise UserError(
                            _(
                                "You can not delete a blanket order with opened "
                                "purchase orders! "
                                "Try to cancel them before."
                            )
                        )
            order.write({"state": "expired"})
        return True

    def action_view_purchase_orders(self):
        purchase_orders = self._get_purchase_orders()
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        if len(purchase_orders) > 0:
            action["domain"] = [("id", "in", purchase_orders.ids)]
            action["context"] = [("id", "in", purchase_orders.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_view_purchase_blanket_order_line(self):
        action = self.env.ref(
            "purchase_blanket_order" ".act_open_purchase_blanket_order_lines_view_tree"
        ).read()[0]
        lines = self.mapped("line_ids")
        if len(lines) > 0:
            action["domain"] = [("id", "in", lines.ids)]
        return action

    @api.model
    def expire_orders(self):
        today = fields.Date.today()
        expired_orders = self.search(
            [("state", "=", "open"), ("validity_date", "<=", today)]
        )
        expired_orders.modified(["validity_date"])
        expired_orders.recompute()

    @api.model
    def _search_original_uom_qty(self, operator, value):
        bo_line_obj = self.env["purchase.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("original_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_ordered_uom_qty(self, operator, value):
        bo_line_obj = self.env["purchase.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("ordered_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_invoiced_uom_qty(self, operator, value):
        bo_line_obj = self.env["purchase.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("invoiced_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_received_uom_qty(self, operator, value):
        bo_line_obj = self.env["purchase.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("received_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_remaining_uom_qty(self, operator, value):
        bo_line_obj = self.env["purchase.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("remaining_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res


class BlanketOrderLine(models.Model):
    _name = "purchase.blanket.order.line"
    _description = "Blanket Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends("original_uom_qty", "price_unit", "taxes_id")
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(
                line.price_unit,
                line.order_id.currency_id,
                line.original_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    name = fields.Char("Description", track_visibility="onchange")
    sequence = fields.Integer()
    order_id = fields.Many2one(
        "purchase.blanket.order", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain=[("purchase_ok", "=", True)],
    )
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure", required=True)
    price_unit = fields.Float(string="Price", required=True, digits=("Product Price"))
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    date_schedule = fields.Date(string="Scheduled Date")
    original_uom_qty = fields.Float(
        string="Original quantity",
        required=True,
        default=1.0,
        digits=("Product Unit of Measure"),
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_quantities",
        store=True,
        digits=("Product Unit of Measure"),
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_quantities",
        store=True,
        digits=("Product Unit of Measure"),
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_quantities",
        store=True,
        digits=("Product Unit of Measure"),
    )
    remaining_qty = fields.Float(
        string="Remaining quantity in base UoM",
        compute="_compute_quantities",
        store=True,
        digits=("Product Unit of Measure"),
    )
    received_uom_qty = fields.Float(
        string="Received quantity",
        compute="_compute_quantities",
        store=True,
        digits=("Product Unit of Measure"),
    )
    purchase_lines = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="blanket_order_line",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company", related="order_id.company_id", store=True, readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", related="order_id.currency_id", readonly=True
    )
    partner_id = fields.Many2one(
        related="order_id.partner_id", string="Vendor", readonly=True
    )
    user_id = fields.Many2one(
        related="order_id.user_id", string="Responsible", readonly=True
    )
    payment_term_id = fields.Many2one(
        related="order_id.payment_term_id", string="Payment Terms", readonly=True
    )

    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", store=True
    )
    price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)

    def _format_date(self, date):
        # format date following user language
        lang_model = self.env["res.lang"]
        lang = lang_model._lang_get(self.env.user.lang)
        date_format = lang.date_format
        return datetime.strftime(fields.Date.from_string(date), date_format)

    def name_get(self):
        result = []
        if self.env.context.get("from_purchase_order"):
            for record in self:
                res = "[%s]" % record.order_id.name
                if record.date_schedule:
                    formatted_date = self._format_date(record.date_schedule)
                    res += " - {}: {}".format(_("Date Scheduled"), formatted_date)
                res += " ({}: {} {})".format(
                    _("remaining"), record.remaining_uom_qty, record.product_uom.name,
                )
                result.append((record.id, res))
            return result
        return super().name_get()

    def _get_display_price(self, product):

        seller = product._select_seller(
            partner_id=self.order_id.partner_id,
            quantity=self.original_uom_qty,
            date=self.order_id.date_start
            and fields.Date.from_string(self.order_id.date_start),
            uom_id=self.product_uom,
        )

        if not seller:
            return

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price,
                product.supplier_taxes_id,
                self.purchase_lines.taxes_id,
                self.company_id,
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and self.order_id.currency_id
            and seller.currency_id != self.order_id.currency_id
        ):
            price_unit = seller.currency_id.compute(
                price_unit, self.order_id.currency_id
            )

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        return price_unit

    @api.onchange("product_id", "original_uom_qty")
    def onchange_product(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if self.product_id:
            name = self.product_id.name
            if not self.product_uom:
                self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
            if self.order_id.partner_id and float_is_zero(
                self.price_unit, precision_digits=precision
            ):
                self.price_unit = self._get_display_price(self.product_id)
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.name = name

            fpos = self.order_id.fiscal_position_id
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                self.taxes_id = fpos.map_tax(
                    self.product_id.supplier_taxes_id.filtered(
                        lambda r: r.company_id.id == company_id
                    )
                )
            else:
                self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

    @api.depends(
        "purchase_lines.order_id.state",
        "purchase_lines.blanket_order_line",
        "purchase_lines.product_qty",
        "purchase_lines.product_uom",
        "purchase_lines.qty_received",
        "purchase_lines.qty_invoiced",
        "original_uom_qty",
        "product_uom",
    )
    def _compute_quantities(self):
        for line in self:
            purchase_lines = line.purchase_lines
            line.ordered_uom_qty = sum(
                pol.product_uom._compute_quantity(pol.product_qty, line.product_uom)
                for pol in purchase_lines
                if pol.order_id.state != "cancel" and pol.product_id == line.product_id
            )
            line.invoiced_uom_qty = sum(
                pol.product_uom._compute_quantity(pol.qty_invoiced, line.product_uom)
                for pol in purchase_lines
                if pol.order_id.state != "cancel" and pol.product_id == line.product_id
            )
            line.received_uom_qty = sum(
                pol.product_uom._compute_quantity(pol.qty_received, line.product_uom)
                for pol in purchase_lines
                if pol.order_id.state != "cancel" and pol.product_id == line.product_id
            )
            line.remaining_uom_qty = line.original_uom_qty - line.ordered_uom_qty
            line.remaining_qty = line.product_uom._compute_quantity(
                line.remaining_uom_qty, line.product_id.uom_id
            )

    def _validate(self):
        try:
            for line in self:
                assert line.price_unit > 0.0, _("Price must be greater than zero")
                assert line.original_uom_qty > 0.0, _(
                    "Quantity must be greater than zero"
                )
        except AssertionError as e:
            raise UserError(e)
