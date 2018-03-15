# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_qty_received(self):
        for line in self:
            if line.product_id.type in ['service'] and\
                    line.product_id.purchase_manual_received_qty:
                line.qty_received = line.qty_received_manually
            else:
                super(PurchaseOrderLine, self)._compute_qty_received()

    def _inverse_qty_received(self):
        for line in self:
            if line.product_id.type in ['service'] and \
                    line.product_id.purchase_manual_received_qty:
                line.qty_received_manually = line.qty_received

    qty_received_manually = fields.Float(string="Manually Received Qty",
                                         copy=False)
    qty_received = fields.Float(inverse='_inverse_qty_received')
    purchase_manual_received_qty = fields.Boolean(
        related='product_id.purchase_manual_received_qty',
        store=True,
        readonly=True
    )
