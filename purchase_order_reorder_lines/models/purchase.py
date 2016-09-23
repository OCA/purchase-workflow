# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'order_id desc, sequence, id'

    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the purchase order.")

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
        Web add 10 to this value for the next sequence
        This value is given to the context of the o2m field
        in the view. So when we create new purchase order lines,
        the sequence is automatically max_sequence + 10
        """
        self.max_line_sequence = (
            max(self.mapped('order_line.sequence') or [0]) + 10)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='compute_max_line_sequence')
