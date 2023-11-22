# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.float_utils import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_stock_move_account_id(self, move):
        self.ensure_one()
        account = move.product_id.get_product_accounts(
            self.partner_id.property_account_position_id
        )["expense"]
        if account:
            result = account
        else:
            result = self.journal_id.default_debit_account
        return result

    def _prepare_invoice_line_from_stock_move(self, move):
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
        account_id = self._get_stock_move_account_id(move)
        data = {
            "invoice_payment_ref": move.name,
            "invoice_origin": self.origin,
            "product_uom_id": move.product_uom.id,
            "product_id": move.product_id.id,
            "account_id": account_id.id,
            "price_unit": move.price_unit,
            "quantity": qty,
            "discount": 0.0,
            # fixme not sure what to do with this
            # "account_analytic_id": move.account_analytic_id.id,
            # "analytic_tag_ids": move.analytic_tag_ids.ids,
            "tax_ids": invoice_line_tax_ids.ids,
            # FIXME: Is this correct?
            "type": self.type,
        }

        return data

    @api.onchange("purchase_vendor_bill_id", "purchase_id")
    def _onchange_purchase_auto_complete(self):
        res = super().purchase_order_change()
        pickings = self.purchase_id.picking_ids.filtered(lambda p: p.state == "done")
        moves = self.env["stock.move"]
        for picking in pickings:
            moves += picking.move_ids_without_package
        moves_to_invoice = moves.filtered(
            lambda m: m.state == "done" and not m.purchase_line_id
        )
        new_lines = self.env["account.move.line"]
        for move in moves_to_invoice:
            data = self._prepare_invoice_line_from_stock_move(move)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        return res
