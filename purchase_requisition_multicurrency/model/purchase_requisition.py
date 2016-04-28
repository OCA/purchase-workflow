# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2014 Camptocamp SA
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
from openerp import models, fields
from openerp.tools import SUPERUSER_ID


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    date_exchange_rate = fields.Date(
        'Exchange rate reference date',
        help="Defines Exchange rate date of Unit price and subtotal "
             "If not set, takes todays exchange rate.")
    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        required=True,
        help="Pricelist that represent the currency for current logistic "
             "request.")
    currency_id = fields.Many2one(
        related='pricelist_id.currency_id',
        comodel_name='res.currency',
        string='Currency')

    def _auto_init(self, cr, context):
        """Fill in the required field with default values.

        This is similar to the solution used in mail_alias.py in the core.

        The installation of the module will succeed with no errors, and the
        column will be required immediately (the previous solution made it
        required only on the first module update after installation).

        """

        # create the column non required
        self._columns['pricelist_id'].required = False
        super(PurchaseRequisition, self)._auto_init(cr, context=context)

        default_pricelist_id = self.pool['product.pricelist'].search(
            cr, SUPERUSER_ID, [('type', '=', 'purchase')], limit=1,
            context=context
        )[0]

        # do not use the ORM, because it would try to recompute fields that are
        # not fully initialized
        cr.execute('''
                   UPDATE purchase_requisition
                   SET pricelist_id = %s
                   WHERE pricelist_id IS NULL;
                   ''', (default_pricelist_id,))

        # make the column required again
        self._columns['pricelist_id'].required = True
        super(PurchaseRequisition, self)._auto_init(cr, context=context)
