# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api
from odoo.tools import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def write(self, values):
        res = super().write(values)
        if 'product_qty' in values or 'product_uom' in values:
            self._propagage_qty_to_moves()
        return res

    def _propagage_qty_to_moves(self):
        for line in self:
            if line.state != 'purchase':
                continue
            for move in line.move_dest_ids | line.move_ids:
                if move.state in ('cancel', 'done'):
                    continue
                if move.product_id != line.product_id:
                    continue
                move.product_uom_qty = line.product_uom_qty
                if float_is_zero(
                        move.product_uom_qty, line.product_uom.rounding
                ):
                    move._action_cancel()
