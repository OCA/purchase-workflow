# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015
#    Francesco OpenCode Apruzzese (<f.apruzzese@apuliasoftware.com>)
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


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.v7
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id,
                                 group_id, context=None):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            cr, uid, order, order_line, picking_id, group_id, context)
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

    @api.onchange('product_id', 'product_uop_qty', 'product_uop_id')
    def on_change_secondary_uom(self):
        if self.product_id:
            try:
                self.product_qty = (self.product_uop_qty /
                                    self.product_id.uop_coeff)
            except ZeroDivisionError:
                pass
