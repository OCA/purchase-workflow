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
