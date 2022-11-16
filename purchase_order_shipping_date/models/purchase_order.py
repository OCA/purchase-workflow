from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    shipping_date = fields.Datetime(
        "Shipping Date", help="Shipping date promised by vendor.", copy=False
    )
