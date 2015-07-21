# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
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
#
#


import openerp.addons.decimal_precision as dp
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    free_postage = fields.Float(
        string='Purchase Free Postage',
        digits_compute=dp.get_precision('Account'),
        help="Expressed in the currency of the supplier's purchase "
             "pricelist.  This is the amount above which the supplier "
             "offers postage fees. 0 means no postage fees.",
    )

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ['free_postage']
