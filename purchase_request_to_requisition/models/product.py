# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, orm


class Product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'purchase_request': fields.boolean(
            'Purchase Request',
            help="Check this box to generate purchase request instead of "
                 "generating requests for quotation from procurement.")
    }
    _defaults = {
        'purchase_request': False
    }

    def _check_request_requisition(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            if product.purchase_request and product.purchase_requisition:
                return False
        return True

    _constraints = [
        (_check_request_requisition,
         'Only one selection of Purchase Request or Purchase Requisition '
         'is allowed', ['purchase_request', 'purchase_requisition'])]
