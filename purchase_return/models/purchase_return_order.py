from datetime import datetime
from itertools import groupby

from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero
from odoo.tools.misc import formatLang


class PurchaseOrderReturn(models.Model):
    _name = "purchase.return.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
                for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.invoice_status = "to invoice"
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
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
    date_calendar_start = fields.Datetime(
        compute="_compute_date_calendar_start", readonly=True, store=True
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
        "Currency Rate",
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
                        "Your quotation contains products from company "
                        "%(product_company)s whereas your quotation belongs to "
                        "company %(quote_company)s. \n"
                        "Please change the company of your quotation or remove "
                        "the products from other companies (%(bad_products)s).",
                        product_company=", ".join(companies.mapped("display_name")),
                        quote_company=order.company_id.display_name,
                        bad_products=", ".join(bad_products.mapped("display_name")),
                    )
                )

    @api.depends("state", "date_order", "date_approve")
    def _compute_date_calendar_start(self):
        for order in self:
            order.date_calendar_start = (
                order.date_approve
                if (order.state in ["purchase", "done"])
                else order.date_order
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
        """ date_planned = the earliest date_planned across all order lines. """
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
        self = self.with_context(ctx)
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
            ].get_fiscal_position(self.partner_id.id)
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
                template_id = ir_model_data.get_object_reference(
                    "purchase_return", "email_template_edi_purchase_return"
                )[1]
            else:
                template_id = ir_model_data.get_object_reference(
                    "purchase_return", "email_template_edi_purchase_return"
                )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                "mail", "email_compose_message_wizard_form"
            )[1]
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

    def print_return(self):
        self.write({"state": "sent"})
        return self.env.ref(
            "purchase_return.report_purchase_return_order"
        ).report_action(self)

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
            default_move_type="in_invoice"
        )
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals["company_id"]).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total
        # amount is negative. We do this after the moves have been created
        # since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(
            lambda m: m.currency_id.round(m.amount_total) < 0
        ).action_switch_invoice_into_refund_credit_note()

        return self.action_view_invoice(moves)

    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order."""
        self.ensure_one()
        move_type = self._context.get("default_move_type", "in_refund")
        journal = (
            self.env["account.move"]
            .with_context(default_move_type=move_type)
            ._get_default_journal()
        )
        if not journal:
            raise UserError(
                _(
                    "Please define an accounting purchase journal for the company %s (%s)."
                )
                % (self.company_id.name, self.company_id.id)
            )

        partner_invoice_id = self.partner_id.address_get(["invoice"])["invoice"]
        invoice_vals = {
            "ref": self.partner_ref or "",
            "move_type": move_type,
            "narration": self.notes,
            "currency_id": self.currency_id.id,
            "invoice_user_id": self.user_id and self.user_id.id,
            "partner_id": partner_invoice_id,
            "fiscal_position_id": (
                self.fiscal_position_id
                or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)
            ).id,
            "payment_reference": "",
            "partner_bank_id": self.partner_id.bank_ids[:1].id,
            "invoice_origin": self.name,
            "invoice_payment_term_id": self.payment_term_id.id,
            "invoice_line_ids": [],
            "company_id": self.company_id.id,
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

    @api.model
    def retrieve_dashboard(self):
        """This function returns the values to populate the custom dashboard in
        the purchase order views.
        """
        self.check_access_rights("read")

        result = {
            "all_to_send": 0,
            "all_waiting": 0,
            "all_late": 0,
            "my_to_send": 0,
            "my_waiting": 0,
            "my_late": 0,
            "all_avg_order_value": 0,
            "all_avg_days_to_purchase": 0,
            "all_total_last_7_days": 0,
            "all_sent_rfqs": 0,
            "company_currency_symbol": self.env.company.currency_id.symbol,
        }

        one_week_ago = fields.Datetime.to_string(
            fields.Datetime.now() - relativedelta(days=7)
        )
        # This query is brittle since it depends on the label values of a selection field
        # not changing, but we don't have a direct time tracker of when a state changes
        query = """SELECT COUNT(1)
                   FROM mail_tracking_value v
                   LEFT JOIN mail_message m ON (v.mail_message_id = m.id)
                   JOIN purchase_return_order po ON (po.id = m.res_id)
                   WHERE m.create_date >= %s
                     AND m.model = 'purchase.return.order'
                     AND m.message_type = 'notification'
                     AND v.old_value_char = 'RFQ'
                     AND v.new_value_char = 'RFQ Sent'
                     AND po.company_id = %s;
                """

        self.env.cr.execute(query, (one_week_ago, self.env.company.id))
        res = self.env.cr.fetchone()
        result["all_sent_rfqs"] = res[0] or 0

        # easy counts
        po = self.env["purchase.return.order"]
        result["all_to_send"] = po.search_count([("state", "=", "draft")])
        result["my_to_send"] = po.search_count(
            [("state", "=", "draft"), ("user_id", "=", self.env.uid)]
        )
        result["all_waiting"] = po.search_count(
            [("state", "=", "sent"), ("date_order", ">=", fields.Datetime.now())]
        )
        result["my_waiting"] = po.search_count(
            [
                ("state", "=", "sent"),
                ("date_order", ">=", fields.Datetime.now()),
                ("user_id", "=", self.env.uid),
            ]
        )
        result["all_late"] = po.search_count(
            [
                ("state", "in", ["draft", "sent", "to approve"]),
                ("date_order", "<", fields.Datetime.now()),
            ]
        )
        result["my_late"] = po.search_count(
            [
                ("state", "in", ["draft", "sent", "to approve"]),
                ("date_order", "<", fields.Datetime.now()),
                ("user_id", "=", self.env.uid),
            ]
        )

        # Calculated values ('avg order value', 'avg days to purchase',
        # and 'total last 7 days') note that 'avg order value' and
        # 'total last 7 days' takes into account exchange rate and current
        # company's currency's precision. Min of currency precision
        # is taken to easily extract it from query.
        # This is done via SQL for scalability reasons
        query = """SELECT
        AVG(COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total)),
        AVG(extract(epoch from age(po.date_approve,po.create_date)/(24*60*60)::decimal(16,2))),
        SUM(
        CASE WHEN po.date_approve >= %s
        THEN COALESCE(po.amount_total / NULLIF(po.currency_rate, 0), po.amount_total)
        ELSE 0 END),
        MIN(curr.decimal_places)
                   FROM purchase_return_order po
                   JOIN res_company comp ON (po.company_id = comp.id)
                   JOIN res_currency curr ON (comp.currency_id = curr.id)
                   WHERE po.state in ('purchase', 'done')
                     AND po.company_id = %s
                """
        self._cr.execute(query, (one_week_ago, self.env.company.id))
        res = self.env.cr.fetchone()
        result["all_avg_order_value"] = round(res[0] or 0, res[3])
        result["all_avg_days_to_purchase"] = round(res[1] or 0, 2)
        result["all_total_last_7_days"] = round(res[2] or 0, res[3])

        return result

    def _send_reminder_mail(self, send_single=False):
        if not self.user_has_groups("purchase.group_send_reminder"):
            return

        template = self.env.ref(
            "purchase.email_template_edi_purchase_reminder", raise_if_not_found=False
        )
        if template:
            orders = self if send_single else self._get_orders_to_remind()
            for order in orders:
                date = order.date_planned
                if date and (
                    send_single
                    or (
                        date - relativedelta(days=order.reminder_date_before_receipt)
                    ).date()
                    == datetime.today().date()
                ):
                    order.with_context(is_reminder=True).message_post_with_template(
                        template.id,
                        email_layout_xmlid="mail.mail_notification_paynow",
                        composition_mode="comment",
                    )

    def send_reminder_preview(self):
        self.ensure_one()
        if not self.user_has_groups("purchase.group_send_reminder"):
            return

        template = self.env.ref(
            "purchase.email_template_edi_purchase_reminder", raise_if_not_found=False
        )
        if template and self.env.user.email and self.id:
            template.with_context(is_reminder=True).send_mail(
                self.id,
                force_send=True,
                raise_exception=False,
                email_values={"email_to": self.env.user.email, "recipient_ids": []},
                notif_layout="mail.mail_notification_paynow",
            )
            return {
                "toast_message": _("A sample email has been sent to %s.")
                % self.env.user.email
            }

    @api.model
    def _get_orders_to_remind(self):
        """When auto sending a reminder mail, only send for unconfirmed purchase
        order and not all products are service."""
        return self.search(
            [
                ("receipt_reminder_email", "=", True),
                ("state", "in", ["purchase", "done"]),
                ("mail_reminder_confirmed", "=", False),
            ]
        ).filtered(
            lambda p: p.mapped("order_line.product_id.product_tmpl_id.type")
            != ["service"]
        )

    def get_confirm_url(self, confirm_type=None):
        """Create url for confirm reminder or purchase reception email for sending
        in mail."""
        if confirm_type in ["reminder", "reception"]:
            param = url_encode(
                {
                    "confirm": confirm_type,
                    "confirmed_date": self.date_planned and self.date_planned.date(),
                }
            )
            return self.get_portal_url(query_string="&%s" % param)
        return self.get_portal_url()

    def get_update_url(self):
        """Create portal url for user to update the scheduled date on purchase
        order lines."""
        update_param = url_encode({"update": "True"})
        return self.get_portal_url(query_string="&%s" % update_param)

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

    def _confirm_reception_mail(self):
        for order in self:
            if (
                order.state in ["purchase", "done"]
                and not order.mail_reception_confirmed
            ):
                order.mail_reception_confirmed = True
                order.message_post(
                    body=_("The order receipt has been acknowledged by %s.")
                    % order.partner_id.name
                )

    def _update_date_planned_for_lines(self, updated_dates):
        # create or update the activity
        activity = self.env["mail.activity"].search(
            [
                ("summary", "=", _("Date Updated")),
                ("res_model_id", "=", "purchase.return.order"),
                ("res_id", "=", self.id),
                ("user_id", "=", self.user_id.id),
            ],
            limit=1,
        )
        if activity:
            self._update_update_date_activity(updated_dates, activity)
        else:
            self._create_update_date_activity(updated_dates)

        # update the date on PO line
        for line, date in updated_dates:
            line._update_date_planned(date)

    def _create_update_date_activity(self, updated_dates):
        note = (
            _("<p> %s modified receipt dates for the following products:</p>")
            % self.partner_id.name
        )
        for line, date in updated_dates:
            note += _("<p> &nbsp; - %s from %s to %s </p>") % (
                line.product_id.display_name,
                line.date_planned.date(),
                date.date(),
            )
        activity = self.activity_schedule(
            "mail.mail_activity_data_warning",
            summary=_("Date Updated"),
            user_id=self.user_id.id,
        )
        # add the note after we post the activity because the note can be soon
        # changed when updating the date of the next PO line. So instead of
        # sending a mail with incomplete note, we send one with no note.
        activity.note = note
        return activity

    def _update_update_date_activity(self, updated_dates, activity):
        for line, date in updated_dates:
            activity.note += _("<p> &nbsp; - %s from %s to %s </p>") % (
                line.product_id.display_name,
                line.date_planned.date(),
                date.date(),
            )
