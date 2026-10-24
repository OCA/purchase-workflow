# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from markupsafe import Markup

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_return_id = fields.Many2one(
        "purchase.return.order",
        store=False,
        string="Purchase Return Order",
        copy=False,
        help="Auto-complete from a past purchase return order.",
    )

    def _get_invoice_reference(self):
        self.ensure_one()
        vendor_refs = [
            ref
            for ref in set(
                self.line_ids.mapped("purchase_return_line_id.order_id.name")
            )
            if ref
        ]
        if self.ref:
            return [
                ref for ref in self.ref.split(", ") if ref and ref not in vendor_refs
            ] + vendor_refs
        return vendor_refs

    @api.onchange("purchase_return_id")
    def _onchange_purchase_return_auto_complete(self):
        # COPY Logic from account.move._onchange_purchase_order_auto_complete
        if not self.purchase_return_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_return_id.with_company(
            self.purchase_return_id.company_id
        )._prepare_invoice()
        has_invoice_lines = bool(
            self.invoice_line_ids.filtered(
                lambda x: x.display_type not in ("line_note", "line_section")
            )
        )
        new_currency_id = (
            self.currency_id if has_invoice_lines else invoice_vals.get("currency_id")
        )
        del invoice_vals["ref"], invoice_vals["payment_reference"]
        del invoice_vals["company_id"]  # avoid recomputing the currency
        if self.move_type == invoice_vals["move_type"]:
            del invoice_vals[
                "move_type"
            ]  # no need to be updated if it's same value, to avoid recomputes
        self.update(invoice_vals)
        self.currency_id = new_currency_id

        # Copy purchase return lines.
        po_lines = self.purchase_return_id.order_line - self.invoice_line_ids.mapped(
            "purchase_return_line_id"
        )
        self._add_purchase_order_lines(po_lines)

        # Compute invoice_origin.
        origins = set(
            self.invoice_line_ids.mapped("purchase_return_line_id.order_id.name")
        )
        self.invoice_origin = ",".join(list(origins))

        # Compute ref.
        refs = self._get_invoice_return_reference()
        self.ref = ", ".join(refs)

        # Compute payment_reference.
        if not self.payment_reference:
            if len(refs) == 1:
                self.payment_reference = refs[0]
            elif len(refs) > 1:
                self.payment_reference = refs[-1]

        # Copy company_id (only changes if the id is of a child company (branch))
        if self.company_id != self.purchase_id.company_id:
            self.company_id = self.purchase_id.company_id

        self.purchase_return_id = False
        self.partner_bank_id = (
            self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]
        )

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super().create(vals_list)
        for move in moves:
            if move.reversed_entry_id:
                continue
            purchases = (
                move.line_ids.purchase_return_line_id.order_id
                or move.line_ids.purchase_line_id.order_id
            )
            if not purchases:
                continue
            refs = [purchase._get_html_link() for purchase in purchases]
            message = self.env._("This vendor bill has been created from: ") + Markup(
                ","
            ).join(refs)
            move.message_post(body=message)
        return moves

    def write(self, vals):
        # OVERRIDE
        old_purchases = [
            move.mapped("line_ids.purchase_return_line_id.order_id")
            or move.mapped("line_ids.purchase_line_id.order_id")
            for move in self
        ]
        res = super().write(vals)
        for i, move in enumerate(self):
            new_purchases = move.mapped(
                "line_ids.purchase_return_line_id.order_id"
            ) or move.mapped("line_ids.purchase_line_id.order_id")
            if not new_purchases:
                continue
            diff_purchases = new_purchases - old_purchases[i]
            if diff_purchases:
                refs = [purchase._get_html_link() for purchase in diff_purchases]
                message = self.env._(
                    "This vendor bill has been modified from: "
                ) + Markup(",").join(refs)
                move.message_post(body=message)
        return res
