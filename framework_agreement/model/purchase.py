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
        'Portfolio',
        domain="[('supplier_id', '=', partner_id)]",
        help='When a portfolio is selected, the pricelist selection is '
        'restricted to agreements belonging to it. Moreover, some fields '
        'of the order cannot be changed because they their values are set in '
        'the agreement.'
    )

    @api.onchange('pricelist_id')
    def propagate_agreement_fields(self):
        self.currency_id = self.pricelist_id.currency_id

        pricelist = self.pricelist_id
        if pricelist.portfolio_id:
            # self.write does not work in an onchange
            self.payment_term_id = pricelist.payment_term_id
            self.terms_of_payment = pricelist.terms_of_payment
            self.incoterm_id = pricelist.incoterm_id
            self.incoterm_address = pricelist.incoterm_address
            self.origin_address_id = pricelist.origin_address_id
            self.dest_address_id = pricelist.dest_address_id
            self.picking_type_id = pricelist.picking_type_id

    @api.onchange('portfolio_id')
    def onchange_portfolio(self):
        if self.pricelist_id:
            if self.portfolio_id:
                if not self.pricelist_id.portfolio_id:
                    self.pricelist_id = False
            else:
                if self.pricelist_id.portfolio_id:
                    self.pricelist_id = False

    @api.multi
    def onchange_partner_id(self, partner_id):
        """Prevent changes to the supplier if the portfolio is set.

        We use web_context_tunnel in order to keep the original signature.
        """
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        if self.env.context.get('portfolio_id'):
            raise exceptions.Warning(
                _('You cannot change the supplier: '
                  'the PO is linked to an agreement portfolio.')
            )
        return res

    @api.multi
    def write(self, vals):
        return super(PurchaseOrder, self.with_context(block_if_negative_available=True)).write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
