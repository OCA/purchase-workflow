# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import osv, fields
import decimal_precision as dp


#----------------------------------------------------------
#  Stock Move
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = { 
        'landed_cost_line_ids': fields.one2many('landed.cost.position', 'purchase_order_line_id', 'Landed Costs Positions'),
    }

stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = { 
        'landed_cost_line_ids': fields.one2many('landed.cost.position', 'purchase_order_line_id', 'Landed Costs Positions'),
    }

stock_picking()


