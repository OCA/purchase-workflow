# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in purchase order lines.
        Then we add 1 to this value for the next sequence which is given
        to the context of the o2m field in the view. So when we create a new
        purchase order line, the sequence is automatically max_sequence + 1
        """
        for purchase in self:
            purchase.max_line_sequence = (
                max(purchase.mapped('order_line.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    @api.multi
    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        self._reset_sequence()
        return res

    @api.multi
    def copy(self, default=None):
        return super(PurchaseOrder,
                     self.with_context(keep_line_sequence=True)).copy(default)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'sequence, id'

    sequence = fields.Integer(help="Gives the sequence of the line when "
                                   "displaying the purchase order.",
                              default=9999)

    sequence2 = fields.Integer(help="Displays the sequence of the line in "
                               "the purchase order.",
                               related='sequence', readonly=True)

    @api.multi
    def _create_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move, line in zip(res, self):
            move.write({'sequence': line.sequence})
        return res

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        # We do reset the sequence if we are copying a complete purchase
        # order
        if self.env.context.get('keep_line_sequence'):
            line.order_id._reset_sequence()
        return line
