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
    )

    @api.onchange('pricelist_id')
    def update_currency_from_pricelist(self):
        """Reproduce the old_api onchange_pricelist from the purchase module.

        We need new-style onchanges to be able to modify agreements on order
        lines, and we cannot have new-style and old-style onchanges at the same
        time.

        """
        self.currency_id = self.pricelist_id.currency_id

    @api.onchange('portfolio_id', 'pricelist_id', 'date_order', 'incoterm_id')
    def update_agreements_in_lines(self):
        Agreement = self.env['framework.agreement']
        if self.portfolio_id:
            for line in self.order_line:
                ag_domain = Agreement.get_agreement_domain(
                    line.product_id.id,
                    line.product_qty,
                    self.portfolio_id.id,
                    self.date_order,
                    self.incoterm_id.id,
                )
                good_agreements = Agreement.search(ag_domain).filtered(
                    lambda a: a.has_currency(self.currency_id))

                if line.framework_agreement_id in good_agreements:
                    pass  # it's good! let's keep it!
                else:
                    if len(good_agreements) == 1:
                        line.framework_agreement_id = good_agreements
                    else:
                        line.framework_agreement_id = Agreement

                if line.framework_agreement_id:
                    line.price_unit = line.framework_agreement_id.get_price(
                        line.product_qty, self.currency_id)
        else:
            self.order_line.write({'framework_agreement_id': False})

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

    @api.multi
    def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft'):
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id,
            product_id,
            qty,
            uom_id,
            partner_id,
            date_order=date_order,
            fiscal_position_id=fiscal_position_id,
            date_planned=date_planned,
            name=name,
            price_unit=price_unit,
        )
        context = self.env.context
        if 'domain' not in res:
            res['domain'] = {}

        if not context.get('portfolio_id') or not product_id:
            res['domain']['framework_agreement_id'] = [('id', '=', 0)]
            res['value']['framework_agreement_id'] = False
            return res

        currency = self.env['res.currency'].browse(context.get('currency_id'))
        Agreement = self.env['framework.agreement']
        agreement = Agreement.browse(context.get('agreement_id'))

        ag_domain = Agreement.get_agreement_domain(
            product_id,
            qty,
            context['portfolio_id'],
            date_planned,
            context.get('incoterm_id'),
        )
        res['domain']['framework_agreement_id'] = ag_domain

        good_agreements = Agreement.search(ag_domain).filtered(
            lambda a: a.has_currency(currency))

        if agreement in good_agreements:
            pass  # it's good! let's keep it!
        else:
            if len(good_agreements) == 1:
                agreement = good_agreements
            else:
                agreement = Agreement

        if agreement:
            res['value']['price_unit'] = agreement.get_price(qty, currency)
        res['value']['framework_agreement_id'] = agreement.id
        return res

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        if self.framework_agreement_id:
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

        if self.framework_agreement_id:
            agreement = self.framework_agreement_id
            if agreement.supplier_id != self.order_id.partner_id:
                raise exceptions.Warning(
                    _('Invalid agreement '
                      'Agreement and supplier does not match')
                )

            self.price_unit = agreement.get_price(self.product_qty,
                                                  self.order_id.currency_id)
