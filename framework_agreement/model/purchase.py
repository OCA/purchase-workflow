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
        PROPAGATE_FIELDS = [
            'currency_id',
            'payment_term_id',
            'terms_of_payment',
            'incoterm_id',
            'incoterm_address',
            'origin_address_id',
            'dest_address_id',
            'picking_type_id',
        ]
        agreement = self.pricelist_id

        for field_name in PROPAGATE_FIELDS:
            # self.write does not work in an onchange
            field_value = agreement[field_name]
            if field_value:
                self[field_name] = field_value

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


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def insufficient_agreed_quantity(self):
        self.ensure_one()
        if not self.order_id.portfolio_id:
            return False

        for product_line in self.order_id.portfolio_id.line_ids:
            if product_line.product_id == self.product_id:
                return self.product_qty > product_line.available_quantity
        raise exceptions.Warning(_(
            'The selected portfolio does not cover product %s'
            % self.product_id.name
        ))

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty,
                            uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draftpo',
                            context=None):

        if context.get('portfolio_id') and not context.get('pricelist_id'):
            return {'warning': {
                'title': _('Warning'),
                'message': _('Since an Agreement Portfolio is selected, '
                             'please select an Agreement in the Pricelist '
                             'field.'),
            }}

        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order, fiscal_position_id, date_planned, name, price_unit,
            context=context)

        return res
