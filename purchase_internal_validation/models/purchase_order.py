# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.tools.translate import _
from openerp.osv import orm, fields


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('sent', 'RFQ Sent'),
        ('wait_valid', 'Waiting for Validation'),
        ('wait_correct', 'Waiting for Correction'),
        ('wait', 'Waiting'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    _columns = {
        'state': fields.selection(
            STATE_SELECTION, 'State', readonly=True,
            help="The state of the purchase order or the quotation request. "
                 "A quotation is a purchase order in a 'Draft' state. "
                 "Then the order has to be confirmed by the user, the state "
                 "switch to 'Confirmed'. Then the supplier must confirm the "
                 "order to change the state to 'Approved'. When the purchase "
                 "order is paid and received, the state becomes 'Done'. "
                 "If a cancel action occurs in the invoice or in the "
                 "reception of goods, the state becomes in exception.",
            select=True)
    }

    # TODO: implement messages system
    def wkf_wait_validation_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise orm.except_orm(
                    _('Error'),
                    _('You can not wait for purchase order to be validated '
                      'without Purchase Order Lines.'))
            for line in po.order_line:
                if line.state == 'draft':
                    todo.append(line.id)
            message = _(
                "Purchase order '%s' is waiting for validation."
            ) % (po.name,)
            self.log(cr, uid, po.id, message)
        for id in ids:
            self.write(cr, uid, [id], {'state': 'wait_valid'})
        return True

    # TODO: implement messages system
    def wkf_wait_correction(self, cr, uid, ids, context=None):
        for id in ids:
            self.write(cr, uid, [id], {'state': 'wait_correct'})
        return True

    # TODO: implement messages system
    def wkf_approved(self, cr, uid, ids, context=None):
        for id in ids:
            self.write(cr, uid, [id], {'state': 'approved'})
        return True
