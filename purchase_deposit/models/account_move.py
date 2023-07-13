# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMove, self).create(vals_list)
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
