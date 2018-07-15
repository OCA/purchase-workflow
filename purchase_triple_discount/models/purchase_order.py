# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _calc_line_base_price(self, line):
        res = super(PurchaseOrderLine, self)._calc_line_base_price(line)
        return res * (1 - line.discount2 / 100.0) *\
            (1 - line.discount3 / 100.0)

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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_inv_line(self, account_id, line):
        res = super(PurchaseOrder, self)._prepare_inv_line(account_id, line)
        res.update({
            'discount2': line.discount2,
            'discount3': line.discount3,
        })
        return res

    @api.model
    def _prepare_order_line_move(
            self, order, order_line, picking_id, group_id):
        res = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        for vals in res:
            vals['price_unit'] = (vals.get('price_unit', 0.0) *
                                  (1 - (order_line.discount2 / 100)) *
                                  (1 - (order_line.discount3 / 100)))
        return res

#    def _get_discounted_price_unit(self):
#        price_unit = super(
#            PurchaseOrderLine, self)._get_discounted_price_unit()
#        if self.discount2:
#            price_unit *= (1 - self.discount2 / 100.0)
#        if self.discount3:
#            price_unit *= (1 - self.discount3 / 100.0)
#        return price_unit
