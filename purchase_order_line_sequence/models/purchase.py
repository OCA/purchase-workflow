# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'order_id desc, sequence, id'

    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the purchase order.")

    sequence2 = fields.Integer(help="Shows the sequence of this line in "
                               "the purchase order.",
                               related='sequence', readonly=True)

    @api.multi
    def _create_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move, line in zip(res, self):
            move.write({'sequence': line.sequence})
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.depends('order_line')
    def compute_max_line_sequence(self):
        """Allow to know the highest sequence
        entered in purchase order lines.
        Web add 1 to this value for the next sequence
        This value is given to the context of the o2m field
        in the view. So when we create new purchase order lines,
        the sequence is automatically max_sequence + 1
        """
        self.max_line_sequence = (
            max(self.mapped('order_line.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='compute_max_line_sequence')
