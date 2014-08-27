# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013 Camptocamp SA
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
from openerp.tools.translate import _


class purchase_cancel(orm.Model):
    _name = "purchase.cancelreason"
    _columns = {
        'name': fields.char('Reason', size=64, required=True, translate=True),
        'type': fields.selection([('rfq', 'RFQ/Bid'), ('purchase', 'Purchase Order')], 'Type', required=True),
        'nounlink': fields.boolean('No unlink'),
    }

    def unlink(self, cr, uid, ids, context=None):
        """ Prevent to unlink records that are used in the code
        """
        unlink_ids = []
        for value in self.read(cr, uid, ids, ['nounlink'], context=context):
            if not value['nounlink']:
                unlink_ids.append(value['id'])
        if unlink_ids:
            return super(purchase_cancel, self).unlink(cr, uid, unlink_ids, context=context)
        return True
