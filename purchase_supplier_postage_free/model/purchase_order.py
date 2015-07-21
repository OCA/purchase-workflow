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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    free_postage = fields.Float(
        compute='_compute_free_postage',
        string='Free Postage',
        digits_compute=dp.get_precision('Account'),
        help="Amount above which the supplier offers postage fees in the "
             "currency of the purchase order.",
    )
    free_postage_reached = fields.Boolean(
        compute='_compute_free_postage',
        string='Free Postage Reached',
        store=True,
        help="If the free postage amount is reached or not. This field "
             "is refreshed when the purchase order is saved.",
    )

    @api.one
    @api.depends('amount_untaxed', 'partner_id', 'pricelist_id',
                 'partner_id.free_postage',
                 'partner_id.property_product_pricelist_purchase',
                 'pricelist_id.currency_id',
                 )
    def _compute_free_postage(self):
        supplier = self.partner_id
        order_currency = self.pricelist_id.currency_id
        threshold = self._get_free_postage_amount(supplier, order_currency)
        if threshold:
            cmp_result = order_currency.compare_amounts(self.amount_untaxed,
                                                        threshold)
            threshold_reached = cmp_result != -1
        else:
            threshold_reached = False
        self.free_postage = threshold
        self.free_postage_reached = threshold_reached

    @api.multi
    def _get_free_postage_amount(self, supplier, order_currency):
        self.ensure_one()
        amount = supplier.free_postage
        supplier_pricelist = supplier.property_product_pricelist_purchase
        supplier_currency = supplier_pricelist.currency_id
        if supplier_currency != order_currency:
            amount = supplier_currency.compute(amount, order_currency)
        return amount
