from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_order_weight_in_po = fields.Boolean(
        "Display Order Weight in PO",
        default=True,
    )
    display_order_volume_in_po = fields.Boolean(
        "Display Order Volume in PO",
        default=True,
    )
