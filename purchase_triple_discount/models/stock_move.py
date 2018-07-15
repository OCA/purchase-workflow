# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        res = super(StockMove, self)._get_invoice_line_vals(
            move, partner, inv_type)
        order_line = False
        if move.purchase_line_id:
            order_line = move.purchase_line_id
        elif move.origin_returned_move_id.purchase_line_id:
            order_line = move.origin_returned_move_id.purchase_line_id
        if order_line:
            res.update({
                'discount2': order_line.discount2,
                'discount3': order_line.discount3,
            })
        return res
