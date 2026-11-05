from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    hide_purchase_price = fields.Boolean(
        string="Hide Prices",
        help="Hide purchase prices for this vendor and for users belong "
        "to 'Purchase hide prices' group.",
    )
