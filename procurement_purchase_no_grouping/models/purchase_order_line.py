# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context and context.get('not_group', False):
            product_id = False
            for arg in args:
                if arg[0] == 'product_id':
                    product_id = arg[2]
                    break
            if product_id:
                product = self.pool['product.product'].browse(
                    cr, uid, product_id, context=context)
                if not product.categ_id.group_on_procured_purchases:
                    return []
        return super(PurchaseOrderLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
