# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """In the case that taxes rounding is set to globally, Odoo requires
        again the line price unit, and currently ORM mixes values, so the only
        way to get a proper value is to overwrite that part, losing
        inheritability.
        """
        orders2recalculate = self.filtered(lambda x: (
            x.company_id.tax_calculation_rounding_method ==
            'round_globally' and any(x.mapped('order_line.discount'))
        ))
        super(PurchaseOrder, self)._amount_all()
        for order in orders2recalculate:
            amount_tax = 0
            for line in order.order_line:
                taxes = line.taxes_id.compute_all(
                    line._get_discounted_price_unit(),
                    line.order_id.currency_id,
                    line.product_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_id,
                )
                amount_tax += sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])
                )
            order.update({
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': order.amount_untaxed + amount_tax,
            })


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount')
    def _compute_amount(self):
        for line in self:
            price_unit = False
            # This is always executed for allowing other modules to use this
            # with different conditions than discount != 0
            price = line._get_discounted_price_unit()
            if price != line.price_unit:
                # Only change value if it's different
                price_unit = line.price_unit
                line.price_unit = price
            super(PurchaseOrderLine, line)._compute_amount()
            if price_unit:
                line.price_unit = price_unit

    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
    )

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    @api.multi
    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super(PurchaseOrderLine, self)._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price
