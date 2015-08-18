# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context and context.get('grouping', 'standard') == 'order':
            return []
        return super(PurchaseOrder, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context and context.get('grouping', 'standard') == 'line':
            return []
        return super(PurchaseOrderLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
