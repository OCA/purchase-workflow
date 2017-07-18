# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('discount2', 'discount3')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()

    discount2 = fields.Float(
        'Disc. 2 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )

    discount3 = fields.Float(
        'Disc. 3 (%)',
        digits=dp.get_precision('Discount'),
        default=0.0,
    )

    _sql_constraints = [
        ('discount2_limit', 'CHECK (discount2 <= 100.0)',
         'Discount 2 must be lower than 100%.'),
        ('discount3_limit', 'CHECK (discount3 <= 100.0)',
         'Discount 3 must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        price_unit = super(
            PurchaseOrderLine, self)._get_discounted_price_unit()
        if self.discount2:
            price_unit *= (1 - self.discount2 / 100.0)
        if self.discount3:
            price_unit *= (1 - self.discount3 / 100.0)
        return price_unit
