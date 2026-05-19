# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    purchase_line_id = fields.Many2one(comodel_name="purchase.order.line")
    cost_update_history = fields.Text(readonly=True)
