from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # Legacy rounding in screen behavior
    price_unit = fields.Float(digits="Product Price")
