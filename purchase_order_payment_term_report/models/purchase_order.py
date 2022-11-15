from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    display_payment_terms_in_report = fields.Boolean(
        "Display Payment Terms In Report", default=True
    )
