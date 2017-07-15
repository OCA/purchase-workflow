# -*- coding: utf-8 -*-
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2015-2016 - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        make_po_conditions = {
            'partner_id', 'state', 'picking_type_id', 'company_id',
            'dest_address_id',
        }
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
        # Restrict the empty return for these conditions
        if (context and context.get('grouping', 'standard') == 'line' and
                len(args) == 1 and args[0][0] == 'order_id' and
                args[0][1] == 'in'):
            return []
        return super(PurchaseOrderLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
