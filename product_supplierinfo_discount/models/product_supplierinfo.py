# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PricelistPartnerInfo(models.Model):
    _inherit = "pricelist.partnerinfo"

    @api.onchange('discount', 'price')
    def _get_price_disc(self):
        self.price_with_disc = self.price * (1 - self.discount/100)

    @api.onchange('price_with_disc')
    def _get_discount(self):
        self.price = self.price_with_disc / (1 - self.discount/100)

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))
    price_with_disc = fields.Float(
        string='Price with Discount',
        digits_compute=dp.get_precision('Product Price'))
