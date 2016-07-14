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
from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _get_po_line_values_from_proc(
            self, procurement, partner, company, schedule_date):
        # Include discount in Purchase Order Line created from procurement
        to_ret = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        discount = self.env['purchase.order.line']._get_product_discount(
            procurement.product_id.id, to_ret['product_qty'], partner.id)
        if discount is not None:
            to_ret['discount'] = discount
        return to_ret
