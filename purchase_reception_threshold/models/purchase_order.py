from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_threshold = fields.Float(
        related="company_id.receipt_threshold",
    )
    use_threshold = fields.Boolean(
        related="partner_id.use_threshold",
    )
