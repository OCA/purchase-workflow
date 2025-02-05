from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    weight = fields.Float(required=False)
    volume = fields.Float(required=False)
