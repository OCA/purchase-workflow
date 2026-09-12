from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    container_id = fields.Many2one(
        "purchase.container", string="Container", copy=False, index=True
    )
