# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    portfolio_id = fields.Many2one(
        'framework.agreement.portfolio',
        'Portfolio',
        domain="[('supplier_id', '=', partner_id)]",
    )

    @api.onchange('portfolio_id', 'date_order', 'incoterm_id')
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

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Prevent changes to the supplier if the portfolio is set."""
        res = super(PurchaseOrder, self).onchange_partner_id()
        if self.portfolio_id:
            raise UserError(
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

    def _get_framework_agreement(self):
        agreement_model = self.env['framework.agreement']
        ag_domain = agreement_model.get_agreement_domain(
            self.product_id.id,
            self.product_qty,
            self.portfolio_id.id,
            self.order_id.date_order,
            self.order_id.incoterm_id.id,
        )
        framework_agreement = self.framework_agreement_id
        good_agreements = agreement_model.search(ag_domain).filtered(
            lambda a: a.has_currency(self.order_id.currency_id))
        if len(good_agreements) > 1 \
                and framework_agreement in good_agreements:
            pass  # it's good! let's keep it!
        else:
            if len(good_agreements) == 1:
                framework_agreement = good_agreements
            else:
                framework_agreement = False
        return framework_agreement

    def _get_framework_agreement_price(self):
        if self.framework_agreement_id:
            return self.framework_agreement_id.get_price(
                self.product_qty, currency=self.currency_id)

    @api.onchange('product_id', 'product_qty', 'product_uom')
    def onchange_get_price_unit(self):
        if not self.order_id.portfolio_id or not self.product_id or not \
                self.date_planned:
            pass
        else:
            agreement = self._get_framework_agreement()
            if agreement != self.framework_agreement_id:
                self.framework_agreement_id = agreement
        if self.order_id.portfolio_id:
            if self.framework_agreement_id:
                self.price_unit = self._get_framework_agreement_price()
            else:
                self.price_unit = 0.0

    def _propagate_fields(self):
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
                raise UserError(
                    _('Invalid agreement '
                      'Agreement and supplier does not match'))
            self.price_unit = agreement.get_price(self.product_qty,
                                                  self.order_id.currency_id)

    @api.multi
    @api.constrains('price_unit')
    def _check_line_price_unit_framework_agreement(self):
        for record in self:
            if record.framework_agreement_id:
                agreement_price = record.framework_agreement_id.get_price(
                    record.product_qty,
                    currency=record.currency_id)
                if agreement_price != self.price_unit:
                    msg = _(
                        "In line %s You have set the price to %s \n"
                        " but there is a running agreement"
                        " with price %s") % (
                        record.name, record.price_unit, agreement_price)
                    raise UserError(msg)
