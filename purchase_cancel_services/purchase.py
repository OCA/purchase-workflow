# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _


class purchase_order(orm.Model):

    _inherit = 'purchase.order'

    def has_services(self, cr, uid, ids, *args):
        res = False
        for order in self.browse(cr, uid, ids):
            if order.invoice_method != 'picking':
                return False
            for order_line in order.order_line:
                if order_line.invoiced:
                    return False
                if (order_line.product_id
                    and order_line.product_id.type == 'service') \
                        or not order_line.product_id:
                    res = True
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        for purchase in self.browse(cr, uid, ids, context=context):
            for order_line in purchase.order_line:
                if order_line.invoiced:
                    raise orm.except_orm(
                        _('Unable to cancel this purchase order.'),
                        _('Invoices have already been created.'))
        super(purchase_order, self).action_cancel(cr, uid, ids,
                                                  context=context)