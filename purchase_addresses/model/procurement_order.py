# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def create_procurement_purchase_order(self,
                                          procurement,
                                          po_vals,
                                          line_vals):
        po_vals.update({'consignee_id': procurement.consignee_id.id,
                        'origin_address_id': po_vals['partner_id'],
                        })
        _super = super(ProcurementOrder, self)
        return _super.create_procurement_purchase_order(procurement,
                                                        po_vals,
                                                        line_vals)
