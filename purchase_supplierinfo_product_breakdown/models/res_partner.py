from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_product_components = fields.Boolean()
