# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone
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

from openerp import models, fields, api
from openerp import exceptions, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    portfolio_id = fields.Many2one(
        'framework.agreement.portfolio',
        'Portfolio'
    )


class PurchaseOrderLine(models.Model):
    """Add on change on price to raise a warning if line is subject to
    an agreement.
    """

    _inherit = "purchase.order.line"

    framework_agreement_id = fields.Many2one(
        'framework.agreement',
        'Agreement',
        domain=[('portfolio_id', '=', 'order_id.portfolio_id')],
    )

    portfolio_id = fields.Many2one(
        'framework.agreement.portfolio',
        'Portfolio',
        readonly=True,
        related='order_id.portfolio_id',
    )

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        agreement_price = self.framework_agreement_id.get_price(
            self.product_qty,
            currency=self.order_id.pricelist_id.currency_id)
        if agreement_price != self.price_unit:
            msg = _(
                "You have set the price to %s \n"
                " but there is a running agreement"
                " with price %s") % (
                    self.price_unit, agreement_price
            )
            raise exceptions.Warning(msg)
        return {}

    @api.multi
    def _propagate_fields(self):
        self.ensure_one()
        agreement = self.framework_agreement_id

        if agreement.payment_term_id:
            self.payment_term_id = agreement.payment_term_id

        if agreement.incoterm_id:
            self.incoterm_id = agreement.incoterm_id

        if agreement.incoterm_address:
            self.incoterm_address = agreement.incoterm_address

    @api.onchange('framework_agreement_id')
    def onchange_agreement(self):
        self._propagate_fields()

        if isinstance(self.id, models.NewId):
            return
        if self.framework_agreement_id:
            agreement = self.framework_agreement_id
            if agreement.supplier_id.id != self.order_id.partner_id:
                raise exceptions.Warning(
                    _('Invalid agreement '
                      'Agreement and supplier does not match')
                )

            raise exceptions.Warning(
                _('Agreement Warning! '
                  'If you change the agreement of this line'
                  ' prices will not be updated.')
            )
