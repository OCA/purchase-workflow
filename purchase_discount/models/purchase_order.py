# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        # Method copy-pasted from odoo/addons/purchase © Odoo S.A.
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if (
                    order.company_id.tax_calculation_rounding_method ==
                    'round_globally'
                ):
                    # purchase_discount modif below: price_unit uses discount
                    price_unit = line.price_unit * (1 - line.discount / 100.0)
                    taxes = line.taxes_id.compute_all(
                        price_unit, line.order_id.currency_id,
                        line.product_qty, product=line.product_id,
                        partner=line.order_id.partner_id)
                    amount_tax += sum(
                        t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        prices = {}
        for line in self:
            if line.discount:
                prices[line.id] = line.price_unit
                line.price_unit *= (1 - line.discount / 100.0)
        super(PurchaseOrderLine, self)._compute_amount()
        # restore prices
        for line in self:
            if line.discount:
                line.price_unit = prices[line.id]

    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    @api.multi
    def _get_stock_move_price_unit(self):
        # method copy-pasted from odoo/addons/purchase/models/purchase.py
        self.ensure_one()
        line = self[0]
        order = line.order_id
        # The only line modified is the line below
        price_unit = line.price_unit * (1 - line.discount / 100.0)
        if line.taxes_id:
            price_unit = line.taxes_id.with_context(round=False).compute_all(
                price_unit, currency=line.order_id.currency_id,
                quantity=1.0)['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *=\
                line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id.compute(
                price_unit, order.company_id.currency_id, round=False)
        return price_unit
