# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015
#    Francesco OpenCode Apruzzese (<f.apruzzese@apuliasoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        for line in res:
            for purchase_line in order_line:
                if line['purchase_line_id'] == purchase_line.id and\
                        purchase_line.product_uop_id:
                    line['product_uos'] = purchase_line.product_uop_id.id
                    line['product_uos_qty'] = purchase_line.product_uop_qty
        return res


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    product_uop_id = fields.Many2one('product.uom', string='Product UoP')
    product_uop_qty = fields.Float(string='Quantity (UoP)',
                                   default=1.00)
    price_unit_uop = fields.Float(string='Price Unit (UoP)',
                                  digits=dp.get_precision('Product Price'),)

    @api.multi
    def update_uom_price_data(self):
        try:
            self.product_qty = (self.product_uop_qty /
                                self.product_id.uop_coeff)
            self.price_unit = self.price_unit_uop * self.product_id.uop_coeff
        except ZeroDivisionError:
            pass

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id,
                            qty, uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft',
                            context=None):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order, fiscal_position_id, date_planned, name,
            price_unit, state, context)
        if not res:
            return res
        if not product_id:
            return res
        product = self.pool['product.product'].browse(
            cr, uid, product_id, context)
        if product.uop_id:
            res['value'].update(
                {'product_uop_id': product.uop_id.id,
                 'product_uop_qty': (product.uop_coeff * qty) or qty})
        return res
