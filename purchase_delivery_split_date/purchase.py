# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class PurchaseOrder(orm.Model):
    _inherit = "purchase.order"

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False,
                         context=None):
        """Group the Purchase Order's receptions by expected date"""
        picking_ids = []
        delivery_dates = {}
        # Triage the order lines by delivery date
        for line in order_lines:
            if line.date_planned in delivery_dates:
                delivery_dates[line.date_planned].append(line)
            else:
                delivery_dates[line.date_planned] = [line]
        # Process each group of lines
        for lines in delivery_dates.itervalues():
            picking_ids.extend(
                super(PurchaseOrder, self)._create_pickings(
                    cr, uid, order, lines, picking_id=picking_id,
                    context=context))
        return picking_ids
