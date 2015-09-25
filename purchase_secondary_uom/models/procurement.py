# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015
#    Andrea Gallina (<a.gallina@apuliasoftware.it>)
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

from openerp import models, fields, api, _


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.v7
    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner,
                                      company, schedule_date, context=None):
        res = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            cr, uid, procurement, partner, company, schedule_date, context)
        if not res:
            return res
        product_id = res.get('product_id', False)
        if not product_id:
            return res
        qty = res.get('product_qty', 1.0)
        product = self.pool['product.product'].browse(
            cr, uid, product_id, context)
        if product.uop_id:
            res.update({'product_uop_id': product.uop_id.id,
                        'product_uop_qty': (product.uop_coeff * qty) or qty})
        return res
