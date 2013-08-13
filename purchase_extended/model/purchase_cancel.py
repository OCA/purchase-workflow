# -*- coding: utf-8 -*-

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
