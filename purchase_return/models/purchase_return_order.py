# Copyright 2004-2021 Odoo S.A.
# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_list, formatLang, groupby
from odoo.tools.float_utils import float_is_zero


class PurchaseOrderReturn(models.Model):
    _name = "purchase.return.order"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Purchase Return Order"
    _rec_names_search = ["name", "partner_ref"]
    _order = "id desc"

    @api.depends("order_line.price_subtotal", "company_id", "currency_id")
    def _compute_amount_all(self):
        AccountTax = self.env["account.tax"]
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [
                line._prepare_base_line_for_taxes_computation() for line in order_lines
            ]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            order.amount_untaxed = tax_totals["base_amount_currency"]
            order.amount_tax = tax_totals["tax_amount_currency"]
            order.amount_total = tax_totals["total_amount_currency"]
            order.amount_total_cc = tax_totals["total_amount"]

    @api.depends("state", "order_line.qty_to_invoice")
    def _compute_get_invoiced(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if order.state not in ("purchase", "done"):
                order.invoice_status = "no"
                continue

            if any(
                not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                for line in order.order_line.filtered(lambda obj: not obj.display_type)
            ):
                order.invoice_status = "to invoice"
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(
                        lambda obj: not obj.display_type
                    )
                )
                and order.invoice_ids
            ):
                order.invoice_status = "invoiced"
            else:
                order.invoice_status = "no"

    @api.depends("order_line.invoice_lines.move_id")
    def _compute_invoice(self):
        for order in self:
            invoices = order.mapped("order_line.invoice_lines.move_id")
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    name = fields.Char(
        "Order Reference", required=True, index=True, copy=False, default="New"
    )
    origin = fields.Char(
        "Source Document",
        copy=False,
        help="Reference of the document that generated this purchase order "
        "request (e.g. a sales order)",
    )
    partner_ref = fields.Char(
        "Vendor Reference",
        copy=False,
        help="Reference of the sales order or bid sent by the vendor. "
        "It's used to do the matching when you receive the "
        "products as this reference is usually written on the "
        "delivery order sent by your vendor.",
    )
    date_order = fields.Datetime(
        "Order Deadline",
        required=True,
        index=True,
        copy=False,
        default=fields.Datetime.now,
        help="Depicts the date within which the Quotation should be "
        "confirmed and converted into a purchase order.",
    )
    date_approve = fields.Datetime("Confirmation Date", index=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        required=True,
        index=True,
        change_default=True,
        tracking=True,
        check_company=True,
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )
    dest_address_id = fields.Many2one(
        "res.partner",
        check_company=True,
        string="Drop Ship Address",
        help="Put an address if you want to return directly from the customer "
        "to the vendor. Otherwise, keep empty to deliver from your own "
        "company.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        compute="_compute_currency_id",
        store=True,
        readonly=False,
        precompute=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("to approve", "To Approve"),
            ("purchase", "Purchase Order Return"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    order_line = fields.One2many(
        "purchase.return.order.line", "order_id", string="Order Lines"
    )
    notes = fields.Html("Terms and Conditions")
    invoice_count = fields.Integer(
        compute="_compute_invoice",
        string="Bill Count",
        copy=False,
        default=0,
        store=True,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_invoice",
        string="Bills",
        copy=False,
        store=True,
    )
    invoice_status = fields.Selection(
        [
            ("no", "Nothing to Refund"),
            ("to invoice", "Waiting Refunds"),
            ("invoiced", "Fully Refunded"),
        ],
        string="Billing Status",
        compute="_compute_get_invoiced",
        store=True,
        copy=False,
        default="no",
    )
    date_planned = fields.Datetime(
        string="Issue Date",
        index=True,
        copy=False,
        compute="_compute_date_planned",
        store=True,
        readonly=False,
        help="Delivery date to return to the vendor. This date is used to "
        "determine expected shipment of products.",
    )

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        compute="_compute_amount_all",
        tracking=True,
    )
    tax_totals = fields.Binary(compute="_compute_tax_totals", exportable=False)
    amount_tax = fields.Monetary(
        string="Taxes", store=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, compute="_compute_amount_all"
    )
    amount_total_cc = fields.Monetary(
        string="Company Total",
        store=True,
        compute="_compute_amount_all",
        currency_field="company_currency_id",
    )

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        check_company=True,
    )
    tax_calculation_rounding_method = fields.Selection(
        related="company_id.tax_calculation_rounding_method",
        string="Tax calculation rounding method",
        readonly=True,
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        "Payment Terms",
        check_company=True,
    )
    incoterm_id = fields.Many2one(
        "account.incoterms",
        "Incoterm",
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.",
    )

    product_id = fields.Many2one(
        "product.product",
        related="order_line.product_id",
        string="Product",
        readonly=False,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Purchase Representative",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company.id,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency"
    )
    currency_rate = fields.Float(
        "Rate Currency",
        compute="_compute_currency_rate",
        digits=0,
        store=True,
        precompute=True,
    )

    @api.constrains("company_id", "order_line")
    def _check_order_line_company_id(self):
        for order in self:
            invalid_companies = order.order_line.product_id.company_id.filtered(
                lambda c, order=order: order.company_id not in c._accessible_branches()
            )
            if invalid_companies:
                bad_products = order.order_line.product_id.filtered(
                    lambda p, invalid_companies=invalid_companies: p.company_id
                    and p.company_id in invalid_companies
                )
                raise ValidationError(
                    _(
                        "Your purchase return contains products from company "
                        "%(product_company)s whereas your purchase return "
                        "belongs to "
                        "company %(quote_company)s. \n"
                        "Please change the company of your order or remove "
                        "the products from other companies (%(bad_products)s).",
                        product_company=", ".join(
                            invalid_companies.sudo().mapped("display_name")
                        ),
                        quote_company=order.company_id.display_name,
                        bad_products=", ".join(bad_products.mapped("display_name")),
                    )
                )

    @api.depends("currency_id", "date_order", "company_id")
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env["res.currency"]._get_conversion_rate(
                from_currency=order.company_id.currency_id,
                to_currency=order.currency_id,
                company=order.company_id,
                date=(order.date_order or fields.Datetime.now()).date(),
            )

    @api.depends("order_line.date_planned")
    def _compute_date_planned(self):
        """date_planned = the earliest date_planned across all order lines."""
        for order in self:
            dates_list = order.order_line.filtered(
                lambda x: not x.display_type and x.date_planned
            ).mapped("date_planned")
            if dates_list:
                order.date_planned = min(dates_list)
            else:
                order.date_planned = False

    @api.depends("amount_total", "currency_rate")
    def _compute_amount_total_cc(self):
        for order in self:
            order.amount_total_cc = order.amount_total / order.currency_rate

    @api.depends("name", "partner_ref", "amount_total", "currency_id")
    @api.depends_context("show_total_amount")
    def _compute_display_name(self):
        for po in self:
            name = po.name
            if po.partner_ref:
                name += " (" + po.partner_ref + ")"
            if self.env.context.get("show_total_amount") and po.amount_total:
                name += ": " + formatLang(
                    self.env, po.amount_total, currency_obj=po.currency_id
                )
            po.display_name = name

    @api.depends_context("lang")
    @api.depends("order_line.price_subtotal", "currency_id", "company_id")
    def _compute_tax_totals(self):
        AccountTax = self.env["account.tax"]
        for order in self:
            if not order.company_id:
                order.tax_totals = False
                continue
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [
                line._prepare_base_line_for_taxes_computation() for line in order_lines
            ]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            if order.currency_id != order.company_currency_id:
                amount_cc = formatLang(
                    self.env,
                    order.amount_total_cc,
                    currency_obj=order.company_currency_id,
                )
                order.tax_totals["amount_total_cc"] = f"({amount_cc})"

    @api.onchange("date_planned")
    def onchange_date_planned(self):
        if self.date_planned:
            self.order_line.filtered(
                lambda line: not line.display_type
            ).date_planned = self.date_planned

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get(
                "company_id", self.default_get(["company_id"])["company_id"]
            )
            # Ensures default picking type and
            # currency are taken from the right company.
            self_comp = self.with_company(company_id)
            if vals.get("name", "New") == "New":
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(
                        self, fields.Datetime.to_datetime(vals["date_order"])
                    )
                vals["name"] = (
                    self_comp.env["ir.sequence"].next_by_code(
                        "purchase.return.order", sequence_date=seq_date
                    )
                    or "/"
                )
            return super(PurchaseOrderReturn, self_comp).create([vals])

    @api.ondelete(at_uninstall=False)
    def _unlink_if_cancelled(self):
        for order in self:
            if not order.state == "cancel":
                raise UserError(
                    _("In order to delete a purchase order, you must cancel it first.")
                )

    def copy(self, default=None):
        ctx = dict(self.env.context)
        ctx.pop("default_product_id", None)
        self = self.with_context(**ctx)
        new_po = super().copy(default=default)
        return new_po

    def _must_delete_date_planned(self, field_name):
        # To be overridden
        return field_name == "order_line"

    def onchange(self, values, field_names, fields_spec):
        """
        Override onchange to NOT update all date_planned on PO lines when
        date_planned on PO is updated by the change of date_planned on PO lines.
        """
        result = super().onchange(values, field_names, fields_spec)
        if (
            any(self._must_delete_date_planned(field) for field in field_names)
            and "value" in result
        ):
            for line in result["value"].get("order_line", []):
                if line[0] == Command.UPDATE and "date_planned" in line[2]:
                    del line[2]["date_planned"]
        return result

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "purchase":
            if init_values["state"] == "to approve":
                return self.env.ref("purchase_return.mt_return_approved")
            return self.env.ref("purchase_return.mt_return_confirmed")
        elif "state" in init_values and self.state == "to approve":
            return self.env.ref("purchase_return.mt_return_confirmed")
        elif "state" in init_values and self.state == "done":
            return self.env.ref("purchase_return.mt_return_done")
        return super()._track_subtype(init_values)

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"Purchase Order Return-{self.name}"

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        # Ensures all properties and fiscal positions
        # are taken with the company of the order
        # if not defined, with_company doesn't change anything.
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.fiscal_position_id = False
        else:
            self.fiscal_position_id = self.env[
                "account.fiscal.position"
            ]._get_fiscal_position(self.partner_id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            self.currency_id = (
                self.partner_id.property_purchase_currency_id.id
                or self.env.company.currency_id.id
            )
        return {}

    @api.depends("partner_id", "company_id")
    def _compute_currency_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            if not order.partner_id:
                order.currency_id = order.company_id.currency_id
            else:
                order.currency_id = (
                    order.partner_id.property_purchase_currency_id
                    or order.company_id.currency_id
                )

    @api.onchange("fiscal_position_id", "company_id")
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the PO.
        """
        self.order_line._compute_tax_id()

    def action_draft_send(self):
        """
        This function opens a window to compose an email, with the edi
        purchase template message loaded by default
        """
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]
        try:
            if self.env.context.get("send_draft", False):
                template_id = ir_model_data._xmlid_lookup(
                    "purchase_return.email_template_edi_purchase_return"
                )[1]
            else:
                template_id = ir_model_data._xmlid_lookup(
                    "purchase_return.email_template_edi_purchase_return"
                )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                "mail.email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        email_layout_xmlid = "mail.mail_notification_layout_with_responsible_signature"
        ctx.update(
            {
                "default_model": "purchase.return.order",
                "default_res_ids": self.ids,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": email_layout_xmlid,
                "email_notification_allow_footer": True,
                "force_email": True,
                "mark_rfq_as_sent": True,
            }
        )

        # In the case of a RFQ or a PO, we want the "View..." button in line
        # with the state of the object. Therefore, we pass the model
        # description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get("lang")
        if {"default_template_id", "default_model", "default_res_id"} <= ctx.keys():
            template = self.env["mail.template"].browse(ctx["default_template_id"])
            if template and template.lang:
                lang = template._render_lang([ctx["default_res_id"]])[
                    ctx["default_res_id"]
                ]

        self = self.with_context(lang=lang)
        if self.state in ["draft", "sent"]:
            ctx["model_description"] = self.env._("Request for Quotation")
        else:
            ctx["model_description"] = self.env._("Purchase Order")

        return {
            "name": self.env._("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_rfq_as_sent"):
            self.filtered(lambda o: o.state == "draft").write({"state": "sent"})
        po_ctx = {
            "mail_post_autofollow": self.env.context.get("mail_post_autofollow", True)
        }
        if self.env.context.get("mark_rfq_as_sent") and "notify_author" not in kwargs:
            kwargs["notify_author"] = self.env.user.partner_id.id in (
                kwargs.get("partner_ids") or []
            )
        return super(PurchaseOrderReturn, self.with_context(**po_ctx)).message_post(
            **kwargs
        )

    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({"state": "purchase", "date_approve": fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == "lock").write({"state": "done"})
        return {}

    def button_draft(self):
        self.write({"state": "draft"})
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ["draft", "sent"]:
                continue
            order.button_approve()
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def button_cancel(self):
        purchase_orders_with_invoices = self.filtered(
            lambda po: any(i.state not in ("cancel", "draft") for i in po.invoice_ids)
        )
        if purchase_orders_with_invoices:
            self.env._(
                "Unable to cancel purchase order(s): %s. "
                "You must first cancel their related vendor bills.",
                format_list(
                    self.env, purchase_orders_with_invoices.mapped("display_name")
                ),
            )
        self.write({"state": "cancel"})

    def button_unlock(self):
        self.write({"state": "purchase"})

    def button_done(self):
        self.write({"state": "done"})

    def print_return(self):
        self.write({"state": "sent"})
        return self.env.ref(
            "purchase_return.report_purchase_return_order"
        ).report_action(self)

    def action_create_refund(self):
        """Create the refund associated to the PO."""
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        sequence = 10
        for order in self:
            if order.invoice_status != "to invoice":
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == "line_section":
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        line_vals = pending_section._prepare_account_move_line()
                        line_vals.update({"sequence": sequence})
                        invoice_vals["invoice_line_ids"].append((0, 0, line_vals))
                        sequence += 1
                        pending_section = None
                    line_vals = line._prepare_account_move_line()
                    line_vals.update({"sequence": sequence})
                    invoice_vals["invoice_line_ids"].append((0, 0, line_vals))
                    sequence += 1
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(
                self.env._(
                    "There is no invoiceable line. If a product has a control "
                    "policy based on received quantity, please make sure that a "
                    "quantity has been received."
                )
            )

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for _grouping_keys, invoices in groupby(
            invoice_vals_list,
            key=lambda x: (
                x.get("company_id"),
                x.get("partner_id"),
                x.get("currency_id"),
            ),
        ):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals["invoice_line_ids"] += invoice_vals[
                        "invoice_line_ids"
                    ]
                origins.add(invoice_vals["invoice_origin"])
                payment_refs.add(invoice_vals["payment_reference"])
                refs.add(invoice_vals["ref"])
            ref_invoice_vals.update(
                {
                    "ref": ", ".join(refs)[:2000],
                    "invoice_origin": ", ".join(origins),
                    "payment_reference": len(payment_refs) == 1
                    and payment_refs.pop()
                    or False,
                }
            )
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env["account.move"]
        AccountMove = self.env["account.move"].with_context(
            default_move_type="in_refund"
        )
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals["company_id"]).create(vals)

        return self.action_view_invoice(moves)

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order."""
        self.ensure_one()
        move_type = "in_refund"

        partner_invoice = self.env["res.partner"].browse(
            self.partner_id.address_get(["invoice"])["invoice"]
        )
        partner_bank_id = (
            self.partner_id.commercial_partner_id.bank_ids.filtered_domain(
                [
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", self.company_id.id),
                ]
            )[:1]
        )

        invoice_vals = {
            "ref": self.partner_ref or self.name,
            "move_type": move_type,
            "narration": self.notes,
            "currency_id": self.currency_id.id,
            "partner_id": partner_invoice.id,
            "fiscal_position_id": (
                self.fiscal_position_id
                or self.fiscal_position_id._get_fiscal_position(partner_invoice)
            ).id,
            "payment_reference": "",
            "partner_bank_id": partner_bank_id.id,
            "invoice_origin": self.name,
            "invoice_payment_term_id": self.payment_term_id.id,
            "invoice_line_ids": [],
            "company_id": self.company_id.id,
            "invoice_date": fields.Date.today(),
        }
        return invoice_vals

    def action_view_invoice(self, invoices=False):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.invalidate_model(["invoice_ids"])
            invoices = self.invoice_ids

        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_in_invoice_type"
        )
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result["domain"] = [("id", "in", invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref("account.view_move_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = invoices.id
        else:
            result = {"type": "ir.actions.act_window_close"}

        return result

    def _approval_allowed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        return (
            self.company_id.po_double_validation == "one_step"
            or (
                self.company_id.po_double_validation == "two_step"
                and self.amount_total
                < self.env.company.currency_id._convert(
                    self.company_id.po_double_validation_amount,
                    self.currency_id,
                    self.company_id,
                    self.date_order or fields.Date.today(),
                )
            )
            or self.env.user.has_group("purchase.group_purchase_manager")
        )
