# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            if not line.purchase_line_id.is_deposit:
                continue
            line.purchase_line_id.taxes_id = line.tax_ids
            line.purchase_line_id.price_unit = line.price_unit
        return res

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        if self.env.context.get("advance_deduct_option") == "proportional":
            for move in moves:
                inv_lines = move.invoice_line_ids.filtered(lambda x: x.quantity > 0)
                adv_lines = move.invoice_line_ids.filtered(lambda x: x.quantity < 0)
                inv_untaxed = sum(inv_lines.mapped("price_subtotal"))
                purchases = inv_lines.mapped("purchase_line_id.order_id")
                if purchases:
                    prop = inv_untaxed / purchases.ensure_one().amount_untaxed
                    for line in adv_lines:
                        line.with_context(check_move_validity=False).write(
                            {"quantity": max(-prop, line.quantity)}
                        )
        return moves
