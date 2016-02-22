# -*- coding: utf-8 -*-
# © # © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

from openerp import models
import time


class delivery_carrier(models.Model):

    _inherit = 'delivery.carrier'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        if context is None:
            context = {}
        purchase_order_id = context.get('purchase_order_id', False)
        if not purchase_order_id:
            res = super(delivery_carrier, self).name_get(cr, uid, ids,
                                                         context=context)
        else:
            order = self.pool.get('purchase.order').browse(
                cr, uid, purchase_order_id, context=context)
            currency = order.pricelist_id.currency_id.name or ''
            res = [(r['id'], r['name']+' ('+(str(r['price']))+' '+currency+')')
                   for r in self.read(cr, uid, ids, ['name',
                                                     'price'], context)]
        return res

    def get_price(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        if context is None:
            context = {}
        purchase_obj = self.pool.get('purchase.order')
        grid_obj = self.pool.get('delivery.grid')
        for carrier in self.browse(cr, uid, ids, context=context):
            order_id = context.get('purchase_order_id', False)
            price = False
            available = False
            if order_id:
                order = purchase_obj.browse(cr, uid, order_id, context=context)
                carrier_grid = self.grid_get(
                    cr, uid, [carrier.id], order.company_id.partner_id.id,
                    context)
                if carrier_grid:
                    try:
                        price = grid_obj.get_price_purchase(
                            cr, uid, carrier_grid, order,
                            time.strftime('%Y-%m-%d'), context)
                        available = True
                    except:
                        price = 0.0
            else:
                price = 0.0
            res[carrier.id] = {
                'price': price,
                'available': available
            }
        return res


class delivery_grid(models.Model):

    _inherit = "delivery.grid"

    def get_price_purchase(self, cr, uid, id, order, dt, context=None):
        weight = 0
        volume = 0
        quantity = 0
        total_delivery = 0.0
        product_uom_obj = self.pool.get('product.uom')
        for line in order.order_line:
            if line.state == 'cancel':
                continue
            if line.is_delivery:
                taxes = self.pool['purchase.order']._amount_line_tax(
                    cr, uid, line, context=context)
                total_delivery += line.price_subtotal + taxes
            if not line.product_id or line.is_delivery:
                continue
            q = product_uom_obj._compute_qty(
                cr, uid, line.product_uom.id, line.product_qty,
                line.product_id.uom_id.id)
            weight += (line.product_id.weight or 0.0) * q
            volume += (line.product_id.volume or 0.0) * q
            quantity += q
        total = (order.amount_total or 0.0) - total_delivery
        ctx = context.copy()
        ctx['date'] = order.date_order
        total = self.pool['res.currency'].compute(
            cr, uid, order.currency_id.id, order.company_id.currency_id.id,
            total, context=ctx)
        return self.get_price_from_picking(cr, uid, id, total, weight, volume,
                                           quantity, context=context)
