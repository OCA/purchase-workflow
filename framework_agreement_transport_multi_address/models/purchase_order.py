# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone, Stefan Rijnhart
#    Copyright 2013-2015 Camptocamp SA
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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_propagate_fields(self):
        res = super(PurchaseOrder, self).get_propagate_fields()
        res.append('origin_address_id')
        return res
