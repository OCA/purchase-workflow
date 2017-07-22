# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        orders2recalculate = self.filtered(lambda x: (
            x.company_id.tax_calculation_rounding_method ==
            'round_globally' and any(x.mapped('order_line.discount'))
        ))
        for order in orders2recalculate:
            vals = {}
            for line in order.order_line.filtered('discount'):
                vals[line] = line.price_unit
                line.price_unit = line._get_discounted_price_unit()
            super(PurchaseOrder, order)._amount_all()
            for line in vals.keys():
                line.discount = vals[line]
        super(PurchaseOrder, self - orders2recalculate)._amount_all()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount')
    def _compute_amount(self):
        for line in self:
            # This is always executed for allowing other modules to use this
            # with different conditions than discount != 0
            price_unit = line._get_discounted_price_unit()
            context_changed = False
            if price_unit != line.price_unit:
                prec = line.order_id.currency_id.decimal_places
                company = line.order_id.company_id
                if company.tax_calculation_rounding_method == 'round_globally':
                    prec += 5
                base = round(price_unit * line.product_qty, prec)
                obj = line.with_context(base_values=(base, base, base))
                context_changed = True
            else:
                obj = line
            super(PurchaseOrderLine, obj)._compute_amount()
            if context_changed:
                # We need to update results back, as each recordset has a
                # different environment and thus the values are not considered
                line.update({
                    'price_tax': obj.price_tax,
                    'price_total': obj.price_total,
                    'price_subtotal': obj.price_subtotal,
                })

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
        maximum inheritability. We have to also switch temporarily the order
        state for avoiding an infinite recursion.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            self.order_id.state = 'draft'
            price_unit = self.price_unit
            self.price_unit = price
        price = super(PurchaseOrderLine, self)._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
            self.order_id.state = 'purchase'
        return price
