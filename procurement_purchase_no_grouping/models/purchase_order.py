# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        make_po_conditions = {
            'partner_id', 'state', 'picking_type_id', 'location_id',
            'company_id', 'dest_address_id'}
        # Restrict the empty return for these conditions
        if (context and context.get('grouping', 'standard') == 'order' and
                make_po_conditions.issubset(set(x[0] for x in args))):
            return []
        return super(PurchaseOrder, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        make_po_conditions = {'order_id', 'product_id', 'product_uom'}
        # Restrict the empty return for these conditions
        if (context and context.get('grouping', 'standard') == 'line' and
                make_po_conditions.issubset(set(x[0] for x in args))):
            return []
        return super(PurchaseOrderLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
