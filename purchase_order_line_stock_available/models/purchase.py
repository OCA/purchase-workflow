from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    virtual_available = fields.Float(
        related="product_id.virtual_available", readonly=True
    )
