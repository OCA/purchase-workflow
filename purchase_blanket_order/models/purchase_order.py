# Copyright (C) 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    blanket_order_id = fields.Many2one(
        'purchase.blanket.order', string='Origin blanket order',
        related='order_line.blanket_line_id.order_id',
        readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    blanket_line_id = fields.Many2one('purchase.blanket.order.line',
                                      string='Origin blanket order line')
