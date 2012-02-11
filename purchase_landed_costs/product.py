#  -*- coding: utf-8 -*-
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
from tools.translate import _
        

#----------------------------------------------------------
# Product INHERIT
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'landed_cost'    :fields.boolean('Caculate Landed Costs', help="Checck this if you want to use landed cost calculation for average price for this product"),
    }

    _defaults = {
        'landed_cost'   : _get_default_id,
    } 

    product_template()

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'landed_cost'    :fields.boolean('Caculate Landed Costs', help="Checck this if you want to use landed cost calculation for average price for this catgory"),
    }
        product_category()

