# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _get_move_account_id(self, move):
        self.ensure_one()
        invoice_line_obj = self.env["account.invoice.line"]
        account = invoice_line_obj.get_invoice_line_account(
            "in_invoice",
            move.product_id,
            self.partner_id.property_account_position_id,
            self.env.user.company_id,
        )
        if account:
            account_id = account.id
        else:
            account_id = invoice_line_obj.with_context(
                {"journal_id": self.journal_id.id, "type": "in_invoice"}
            )._default_account()
        return account_id

    @api.multi
    def _prepare_invoice_line_from_move(self, move):
        self.ensure_one()
        qty = move.quantity_done
        flt_comparison = float_compare(
            qty, 0.0, precision_rounding=move.product_uom.rounding
        )
        if flt_comparison <= 0:
            qty = 0.0

        taxes = move.product_id.supplier_taxes_id
        invoice_line_tax_ids = self.env["account.fiscal.position"].map_tax(
            taxes, move.product_id, self.partner_id
        )  # fixme not sure about this
        account_id = self._get_move_account_id(move)
        data = {
            "name": move.name,
            "origin": self.origin,
            "uom_id": move.product_uom.id,
            "product_id": move.product_id.id,
            "account_id": account_id,
            "price_unit": move.price_unit,
            "quantity": qty,
            "discount": 0.0,
            # fixme not sure what to do with this
            # "account_analytic_id": move.account_analytic_id.id,
            # "analytic_tag_ids": move.analytic_tag_ids.ids,
            "invoice_line_tax_ids": invoice_line_tax_ids.ids,
        }

        return data

    @api.onchange("purchase_id")
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        po = self.env["purchase.order"].search([("name", "=", self.origin)])
        moves = po.picking_ids.filtered(
            lambda p: p.state == "done"
        ).move_ids_without_package
        moves_to_invoice = moves.filtered(
            lambda m: m.state == "done" and not m.purchase_line_id
        )
        new_lines = self.env["account.invoice.line"]
        for move in moves_to_invoice:
            data = self._prepare_invoice_line_from_move(move)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        return res
