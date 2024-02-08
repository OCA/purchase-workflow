from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_packaging_level_id = fields.Many2one(
        "product.packaging.level",
    )
