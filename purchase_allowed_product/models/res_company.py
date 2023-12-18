from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    force_only_supplied_product = fields.Boolean(
        string='Force "Use only allowed products" by default'
    )
