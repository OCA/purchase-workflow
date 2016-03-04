# -*- coding: utf-8 -*-
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _calc_line_base_price(self):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._calc_line_base_price()
        return res * (1 - self.discount / 100.0)

    @api.depends('discount')
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()

    discount = fields.Float(
        string='Discount (%)', digits_compute=dp.get_precision('Discount'))

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]
