# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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
##############################################################################

from openerp.osv import orm


class Picking(orm.Model):
    _inherit = 'stock.picking'

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        """
        Deterministically link the invoiced picking to the associated
        invoice lines through the stock move.
        """
        self.pool['account.invoice.line'].write(
            cr, uid, [invoice_line_id],
            {'invoiced_stock_move_id': move_line.id})
        return super(Picking, self)._invoice_line_hook(
            cr, uid, move_line, invoice_line_id)
