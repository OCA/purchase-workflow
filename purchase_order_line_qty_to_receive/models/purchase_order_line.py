# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_to_receive = fields.Float(compute="_compute_qty_to_receive", store=True)

    @api.depends("product_qty", "qty_received")
    def _compute_qty_to_receive(self):
        for line in self:
            line.qty_to_receive = line.product_qty - line.qty_received
