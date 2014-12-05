# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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

from openerp.osv import fields, osv

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'property_account_creditor_price_difference_categ': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            view_load=True,
            help="This account will be used to value price difference between purchase price and cost price."),

    }
product_category()

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'property_account_creditor_price_difference': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            view_load=True,
            help="This account will be used to value price difference between purchase price and cost price."),
    }
product_template()
