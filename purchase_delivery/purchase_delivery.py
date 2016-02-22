# -*- coding: utf-8 -*-
# © # © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

import time
from openerp import fields, models
from openerp.exceptions import Warning


class purchase_order(models.Model):

    _inherit = 'purchase.order'

    carrier_id = fields.Many2one(
        "delivery.carrier", string="Delivery Method",
        help="Complete this field if you plan to invoice the"
        " shipping based on picking.")

    def _amount_line_tax(self, cr, uid, line, context=None):
        line_obj = self.pool['purchase.order.line']
        val = 0.0
        line_price = line_obj._calc_line_base_price(
            cr, uid, line, context=context)
        line_qty = line_obj._calc_line_quantity(
            cr, uid, line, context=context)
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.taxes_id, line_price, line_qty,
                line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def action_picking_create(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be '
        'used for a single id at a time'
        res = super(purchase_order, self).action_picking_create(
            cr, uid, ids, context=context)
        order = self.browse(cr, uid, ids, context)
        self.pool.get('stock.picking').write(
            cr, uid, res, {'carrier_id': order.carrier_id.id}, context=context)
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)
        if partner_id:
            dtype = self.pool.get('res.partner').browse(
                cr, uid, partner_id,
                context=context).property_delivery_carrier.id
            # TDE NOTE: not sure the aded 'if dtype' is valid
            if dtype:
                result['value']['carrier_id'] = dtype
        return result

    def _delivery_unset(self, cr, uid, ids, context=None):
        purchase_obj = self.pool['purchase.order.line']
        line_ids = purchase_obj.search(
            cr, uid, [('order_id', 'in', ids), ('is_delivery', '=', True)],
            context=context)
        purchase_obj.unlink(cr, uid, line_ids, context=context)

    def delivery_set(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('purchase.order.line')
        grid_obj = self.pool.get('delivery.grid')
        carrier_obj = self.pool.get('delivery.carrier')
        acc_fp_obj = self.pool.get('account.fiscal.position')
        self._delivery_unset(cr, uid, ids, context=context)
        currency_obj = self.pool.get('res.currency')
        line_ids = []
        for order in self.browse(cr, uid, ids, context=context):
            grid_id = carrier_obj.grid_get(cr, uid, [order.carrier_id.id],
                                           order.company_id.partner_id.id)
            if not grid_id:
                raise Warning(_('No grid matching for this carrier!'))
            if order.state not in ('draft', 'sent'):
                raise Warning(_('The order state have to be draft to add '
                                'delivery lines.'))
            grid = grid_obj.browse(cr, uid, grid_id, context=context)
            taxes = grid.carrier_id.product_id.taxes_id.filtered(
                lambda t: t.company_id.id == order.company_id.id)
            fpos = order.fiscal_position or False
            taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
            price_unit = grid_obj.get_price_purchase(
                cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context)
            if order.company_id.currency_id.id != \
                    order.pricelist_id.currency_id.id:
                price_unit = currency_obj.compute(
                    cr, uid, order.company_id.currency_id.id,
                    order.pricelist_id.currency_id.id,
                    price_unit, context=dict(context or {},
                                             date=order.date_order))
            values = {
                'order_id': order.id,
                'name': grid.carrier_id.name,
                'product_qty': 1,
                'product_uom': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'is_delivery': True,
                'date_planned': order.date_order,
            }
            line_id = line_obj.create(cr, uid, values, context=context)
            line_ids.append(line_id)
        return line_ids


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    is_delivery = fields.Boolean("Is a Delivery", default=False)
