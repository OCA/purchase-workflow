from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_image_1920 = fields.Binary("Product Image", related="product_id.image_1920")
