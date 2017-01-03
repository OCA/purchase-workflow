# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2015 Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount')
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
