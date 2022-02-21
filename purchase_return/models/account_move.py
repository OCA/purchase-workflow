# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_return_id = fields.Many2one(
        "purchase.return.order",
        store=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
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

        if not self.purchase_return_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_return_id.with_company(
            self.purchase_return_id.company_id
        )._prepare_invoice()
        del invoice_vals["ref"]
        self.update(invoice_vals)

        # Copy purchase return lines.
        po_lines = self.purchase_return_id.order_line - self.line_ids.mapped(
            "purchase_return_line_id"
        )
        new_lines = self.env["account.move.line"]
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped("purchase_return_line_id.order_id.name"))
        self.invoice_origin = ",".join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ", ".join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.purchase_return_id = False
        self._onchange_currency()
        self.partner_bank_id = (
            self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]
        )

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            if move.reversed_entry_id:
                continue
            purchase = move.line_ids.mapped("purchase_return_line_id.order_id")
            if not purchase:
                continue
            refs = [
                "<a href=# data-oe-model=purchase.order data-oe-id=%s>%s</a>"
                % tuple(name_get)
                for name_get in purchase.name_get()
            ]
            message = _("This vendor bill has been created from: %s") % ",".join(refs)
            move.message_post(body=message)
        return moves

    def write(self, vals):
        # OVERRIDE
        old_purchases = [
            move.mapped("line_ids.purchase_return_line_id.order_id") for move in self
        ]
        res = super(AccountMove, self).write(vals)
        for i, move in enumerate(self):
            new_purchases = move.mapped("line_ids.purchase_return_line_id.order_id")
            if not new_purchases:
                continue
            diff_purchases = new_purchases - old_purchases[i]
            if diff_purchases:
                refs = [
                    "<a href=# data-oe-model=purchase.order data-oe-id=%s>%s</a>"
                    % tuple(name_get)
                    for name_get in diff_purchases.name_get()
                ]
                message = _("This vendor bill has been modified from: %s") % ",".join(
                    refs
                )
                move.message_post(body=message)
        return res
