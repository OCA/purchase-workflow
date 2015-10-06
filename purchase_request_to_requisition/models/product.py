# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
##############################################################################
from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_request = fields.Boolean(string='Purchase Request',
                                      help="Check this box to generate "
                                           "purchase request instead of "
                                           "generating requests for "
                                           "quotation from procurement.",
                                      default=False)

    @api.multi
    def _check_request_requisition(self):
        for product in self:
            if product.purchase_request and product.purchase_requisition:
                return False
        return True

    _constraints = [
        (_check_request_requisition,
         'Only one selection of Purchase Request or Call for Bids allowed',
         ['purchase_request', 'purchase_requisition'])]
