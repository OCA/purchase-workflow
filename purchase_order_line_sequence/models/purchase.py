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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line')
    def _compute_max_line_sequence(self):
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
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.write({'sequence': current_sequence})
                current_sequence += 1

    @api.multi
    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        for rec in self:
            rec._reset_sequence()
        return res

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        self2 = self.with_context(keep_line_sequence=True)
        return super(PurchaseOrder, self2).copy(default)

    @api.multi
    def _create_picking(self):
        res = super(PurchaseOrder, self)._create_picking()
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in
                    order.order_line.mapped('product_id.type')]):
                picking = order.picking_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel'))[0]
                for move, line in zip(
                        sorted(picking.move_lines,
                               key=lambda m: m.id), order.order_line):
                    move.write({'sequence': line.sequence})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'order_id desc, sequence, id'

    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the purchase order.",
                              default=9999)

    sequence2 = fields.Integer(help="Shows the sequence of this line in "
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
        # We do not reset the sequence if we are copying a complete purchase
        # order
        if 'keep_line_sequence' not in self.env.context:
            line.order_id._reset_sequence()
        return line

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        if 'keep_line_sequence' not in self.env.context:
            default['sequence'] = 9999
        return super(PurchaseOrderLine, self).copy(default)
