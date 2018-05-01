# -*- coding: utf-8 -*-
#    Authors: Leonardo Pistone
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

from openerp import models, fields, api


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('move_lines', 'move_lines.state', 'move_lines.invoice_state')
    @api.one
    def get_invoice_state(self):
        """Ignore canceled moves when computing the invoiced state.

        This is necessary because when you amend an order to decrease the
        quantity, you get a canceled purchase order line.

        This fix makes sure that the canceled line is not taken into account
        to determine whether the whole order is invoiced. That way the order
        can finally become "done" as expected.
        """
        result = 'none'
        for move in self.move_lines:
            if move.state != 'cancel':
                if move.invoice_state == 'invoiced':
                    result = 'invoiced'
                elif move.invoice_state == '2binvoiced':
                    result = '2binvoiced'
                    break
        self.invoice_state = result

    invoice_state = fields.Selection(compute='get_invoice_state')
