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

from openerp.osv import orm, fields


class PurchaseResetInvoiceMethod(orm.TransientModel):
    _name = 'purchase.reset.invoice_method'
    _columns = {
        'order_id': fields.many2one(
            'purchase.order', 'Order', readonly=True),
        'invoice_method': fields.selection(
            [('manual', 'Based on Purchase Order lines'),
             ('order', 'Based on generated draft invoice'),
             ('picking', 'Based on incoming shipments')],
            'Invoicing Control'),
        }

    def do_reset(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        return wizard.order_id.reset_invoice_method(
            wizard.invoice_method)
