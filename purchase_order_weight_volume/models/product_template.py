from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    weight = fields.Float(required=True)
    volume = fields.Float(required=False)
