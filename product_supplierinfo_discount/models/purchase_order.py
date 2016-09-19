# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
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
from openerp import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange(
        'product_id', 'product_qty', 'product_uom', 'partner_id',
        'date_order',)
    def _compute_discount(self):
        discount = 0
        if self.product_id:
            # Look for a possible discount
            qty_in_product_uom = self.product_qty
            sinfos = self.env['product.supplierinfo'].search(
                [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                 ('name', 'child_of', self.partner_id.
                    commercial_partner_id.id),
                 '|', ('date_start', '=', False),
                 ('date_start', '<=', self.date_order),
                 '|', ('date_end', '=', False),
                 ('date_end', '>=', self.date_order),
                 ], order="min_qty desc")
            for sinfo in sinfos:
                if sinfo.min_qty <= qty_in_product_uom:
                    discount = sinfo.discount
                    break
        self.discount = discount
