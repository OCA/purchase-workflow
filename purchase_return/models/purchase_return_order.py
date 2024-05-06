# Copyright 2004-2021 Odoo S.A.
# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero
from odoo.tools.misc import formatLang


class PurchaseOrderReturn(models.Model):
    _name = "purchase.return.order"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _description = "Purchase Return Order"
    _order = "id desc"

    @api.depends("order_line.price_total")
    def _compute_amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

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
                for line in order.order_line.filtered(
                    lambda l: l.display_type == "product"
                )
            ):
                order.invoice_status = "to invoice"
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(
                        lambda l: l.display_type == "product"
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

    READONLY_STATES = {
        "purchase": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

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
        states=READONLY_STATES,
        index=True,
        copy=False,
        default=fields.Datetime.now,
        help="Depicts the date within which the Quotation should be "
        "confirmed and converted into a purchase order.",
    )
    date_approve = fields.Datetime(
        "Confirmation Date", readonly=1, index=True, copy=False
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        required=True,
        states=READONLY_STATES,
        change_default=True,
        tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )
    dest_address_id = fields.Many2one(
        "res.partner",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string="Drop Ship Address",
        states=READONLY_STATES,
        help="Put an address if you want to return directly from the customer "
        "to the vendor. Otherwise, keep empty to deliver from your own "
        "company.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        states=READONLY_STATES,
        default=lambda self: self.env.company.currency_id.id,
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
        "purchase.return.order.line",
        "order_id",
        string="Order Lines",
        states={"cancel": [("readonly", True)], "done": [("readonly", True)]},
        copy=True,
    )
    notes = fields.Text("Terms and Conditions")
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
        readonly=True,
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
        readonly=True,
        compute="_compute_amount_all",
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        "Payment Terms",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    incoterm_id = fields.Many2one(
        "account.incoterms",
        "Incoterm",
        states={"done": [("readonly", True)]},
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
        states=READONLY_STATES,
        default=lambda self: self.env.company.id,
    )
    currency_rate = fields.Float(
        "Rate Currency",
        compute="_compute_currency_rate",
        compute_sudo=True,
        store=True,
        readonly=True,
        help="Ratio between the purchase order currency and the company currency",
    )

    @api.constrains("company_id", "order_line")
    def _check_order_line_company_id(self):
        for order in self:
            companies = order.order_line.product_id.company_id
            if companies and companies != order.company_id:
                bad_products = order.order_line.product_id.filtered(
                    lambda p: p.company_id and p.company_id != order.company_id
                )
                raise ValidationError(
                    _(
                        "Your purchase return contains products from company "
                        "%(product_company)s whereas your purchase return "
                        "belongs to "
                        "company %(quote_company)s. \n"
                        "Please change the company of your order or remove "
                        "the products from other companies (%(bad_products)s).",
                        product_company=", ".join(companies.mapped("display_name")),
                        quote_company=order.company_id.display_name,
                        bad_products=", ".join(bad_products.mapped("display_name")),
                    )
                )

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("name", operator, name), ("partner_ref", operator, name)]
        return self._search(
            expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid
        )

    @api.depends("date_order", "currency_id", "company_id", "company_id.currency_id")
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = self.env["res.currency"]._get_conversion_rate(
                order.company_id.currency_id,
                order.currency_id,
                order.company_id,
                order.date_order,
            )

    @api.depends("order_line.date_planned")
    def _compute_date_planned(self):
        """date_planned = the earliest date_planned across all order lines."""
        for order in self:
            dates_list = order.order_line.filtered(
                lambda x: not x.display_type and x.date_planned
            ).mapped("date_planned")
            if dates_list:
                order.date_planned = fields.Datetime.to_string(min(dates_list))
            else:
                order.date_planned = False

    @api.depends("name", "partner_ref")
    def name_get(self):
        result = []
        for po in self:
            name = po.name
            if po.partner_ref:
                name += " (" + po.partner_ref + ")"
            if self.env.context.get("show_total_amount") and po.amount_total:
                name += ": " + formatLang(
                    self.env, po.amount_total, currency_obj=po.currency_id
                )
            result.append((po.id, name))
        return result

    @api.onchange("date_planned")
    def onchange_date_planned(self):
        if self.date_planned:
            self.order_line.filtered(
                lambda line: not line.display_type
            ).date_planned = self.date_planned

    @api.model
    def create(self, vals):
        company_id = vals.get(
            "company_id", self.default_get(["company_id"])["company_id"]
        )
        # Ensures default picking type and currency are taken from the right company.
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
        return super(PurchaseOrderReturn, self_comp).create(vals)

    def unlink(self):
        for order in self:
            if not order.state == "cancel":
                raise UserError(
                    _("In order to delete a purchase order, you must cancel it first.")
                )
        return super(PurchaseOrderReturn, self).unlink()

    def copy(self, default=None):
        ctx = dict(self.env.context)
        ctx.pop("default_product_id", None)
        self = self.with_context(**ctx)
        new_po = super(PurchaseOrderReturn, self).copy(default=default)
        return new_po

    def _must_delete_date_planned(self, field_name):
        # To be overridden
        return field_name == "order_line"

    def onchange(self, values, field_name, field_onchange):
        """Override onchange to NOT to update all date_planned on PO lines when
        date_planned on PO is updated by the change of date_planned on PO lines.
        """
        result = super(PurchaseOrderReturn, self).onchange(
            values, field_name, field_onchange
        )
        if self._must_delete_date_planned(field_name) and "value" in result:
            already_exist = [ol[1] for ol in values.get("order_line", []) if ol[1]]
            for line in result["value"].get("order_line", []):
                if (
                    line[0] < 2
                    and "date_planned" in line[2]
                    and line[1] in already_exist
                ):
                    del line[2]["date_planned"]
        return result

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "purchase":
            return self.env.ref("purchase_return.mt_return_approved")
        elif "state" in init_values and self.state == "to approve":
            return self.env.ref("purchase_return.mt_return_confirmed")
        elif "state" in init_values and self.state == "done":
            return self.env.ref("purchase_return.mt_return_done")
        return super(PurchaseOrderReturn, self)._track_subtype(init_values)

    def _get_report_base_filename(self):
        self.ensure_one()
        return "Purchase Order Return-%s" % (self.name)

    @api.onchange("partner_id", "company_id")
    def onchange_partner_id(self):
        # Ensures all properties and fiscal positions
        # are taken with the company of the order
        # if not defined, with_company doesn't change anything.
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.fiscal_position_id = False
            self.currency_id = self.env.company.currency_id.id
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
                )[2]
            else:
                template_id = ir_model_data._xmlid_lookup(
                    "purchase_return.email_template_edi_purchase_return"
                )[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                "mail.email_compose_message_wizard_form"
            )[2]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "default_model": "purchase.return.order",
                "active_model": "purchase.return.order",
                "active_id": self.ids[0],
                "default_res_id": self.ids[0],
                "default_use_template": bool(template_id),
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "custom_layout": "mail.mail_notification_paynow",
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
            ctx["model_description"] = _("Request for Quotation")
        else:
            ctx["model_description"] = _("Purchase Order")

        return {
            "name": _("Compose Email"),
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
        return super(
            PurchaseOrderReturn, self.with_context(mail_post_autofollow=True)
        ).message_post(**kwargs)

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
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ("cancel", "draft"):
                    raise UserError(
                        _(
                            "Unable to cancel this purchase order "
                            "return. You must first cancel the "
                            "related vendor refunds."
                        )
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
                        invoice_vals["invoice_line_ids"].append(
                            (0, 0, pending_section._prepare_account_move_line())
                        )
                        pending_section = None
                    invoice_vals["invoice_line_ids"].append(
                        (0, 0, line._prepare_account_move_line())
                    )
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(
                _(
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
        journal = (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            ._search_default_journal()
        )
        if not journal:
            raise UserError(
                _(
                    "Please define an accounting purchase journal for "
                    "the company %(scn)s (%(sci)s)."
                )
                % {"scn": self.company_id.name, "sci": self.company_id.id}
            )

        partner_invoice_id = self.partner_id.address_get(["invoice"])["invoice"]
        invoice_vals = {
            "ref": self.partner_ref or self.name,
            "move_type": move_type,
            "narration": self.notes,
            "currency_id": self.currency_id.id,
            "invoice_user_id": self.user_id and self.user_id.id,
            "partner_id": partner_invoice_id,
            "fiscal_position_id": (
                self.fiscal_position_id
                or self.fiscal_position_id._get_fiscal_position(self.partner_id)
            ).id,
            "payment_reference": "",
            "partner_bank_id": self.partner_id.bank_ids[:1].id,
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
            self.sudo()._read(["invoice_ids"])
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
            or self.user_has_groups("purchase.group_purchase_manager")
        )
