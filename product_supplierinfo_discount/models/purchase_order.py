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
    def onchange_pol_info(self):
        if self.product_id:
            # Look for a possible discount
            sinfos = self.product_id.seller_ids.filtered(
                lambda r, s=self: (
                    r.name in self.partner_id.commercial_partner_id.
                    child_ids or
                    r.name == self.partner_id.commercial_partner_id) and (
                        r.date_start is False or
                        r.date_start <= self.date_order) and (
                            r.date_end is False or
                            r.date_end >= self.date_order
                ) and r.min_qty <= self.product_qty).sorted(
                    key=lambda s: s.min_qty)
            if sinfos:
                self.discount = sinfos[-1].discount or 0
            else:
                self.discount = 0
