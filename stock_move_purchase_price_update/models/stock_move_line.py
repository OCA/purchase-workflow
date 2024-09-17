# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        compute="_compute_purchase_fields",
    )
    purchase_price_unit = fields.Float(
        string="Purchase price",
        compute="_compute_purchase_fields",
        inverse="_inverse_purchase_price_unit",
        digits="Product Price",
    )
    is_purchase_price_editable = fields.Boolean(
        compute="_compute_purchase_fields",
    )

    @api.depends(
        "move_id.purchase_line_id.price_unit", "move_id.purchase_line_id.qty_invoiced"
    )
    def _compute_purchase_fields(self):
        for line in self:
            line.purchase_line_id = line.move_id.purchase_line_id
            line.purchase_price_unit = line.purchase_line_id.price_unit
            line.is_purchase_price_editable = line.purchase_line_id.qty_invoiced == 0.0

    # Use compute with inverse because related field don't save the value
    def _inverse_purchase_price_unit(self):
        for line in self:
            line.move_id.purchase_line_id.price_unit = line.purchase_price_unit
