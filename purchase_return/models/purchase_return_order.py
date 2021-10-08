from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class PurchaseOrderReturn(models.Model):
    _name = "purchase.return.order"
    _inherit = "purchase.order"
    _description = "Purchase Return Order"
    _order = "id desc"

    order_line = fields.One2many(
        "purchase.return.order.line",
        "order_id",
        string="Order Lines",
        states={"cancel": [("readonly", True)], "done": [("readonly", True)]},
        copy=True,
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

    @api.depends("state", "order_line.qty_to_invoice")
    def _compute_get_invoiced(self):
        self._get_invoiced()

    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_allowed())
        self.write({"state": "purchase", "date_approve": fields.Datetime.now()})
        self.filtered(lambda p: p.company_id.po_lock == "lock").write({"state": "done"})
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ["draft", "sent"]:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({"state": "to approve"})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

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
