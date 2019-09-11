# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    weight_total = fields.Float(string='Total weight')

    @api.onchange('product_id', 'product_id.weight', 'product_qty')
    def _compute_total_weight(self):
        for line in self:
            line.weight_total = line.product_id.weight * \
                line.product_qty

    @api.onchange('product_qty', 'product_uom', 'weight_total')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        super(PurchaseOrderLine, self)._onchange_quantity()
        if self.product_id.compute_price_on_weight:
            seller = self.product_id._select_seller(
                partner_id=self.partner_id,
                quantity=self.product_qty,
                date=self.order_id.date_order and
                self.order_id.date_order[:10],
                uom_id=self.product_uom)

            if seller or not self.date_planned:
                self.date_planned = self._get_date_planned(seller).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)

            if not seller:
                return

            price_unit = self.env['account.tax'].\
                _fix_tax_included_price_company(
                    seller.price * (self.weight_total / self.product_qty if
                                    self.weight_total else
                                    self.product_id.weight),
                    self.product_id.supplier_taxes_id, self.taxes_id,
                    self.company_id) if seller else 0.0
            if price_unit and seller and self.order_id.currency_id \
                    and seller.currency_id != self.order_id.currency_id:
                price_unit = seller.currency_id.compute(
                    price_unit, self.order_id.currency_id)

            if seller and self.product_uom \
                    and seller.product_uom != self.product_uom:
                price_unit = seller.product_uom._compute_price(
                    price_unit, self.product_uom)

            self.price_unit = price_unit
