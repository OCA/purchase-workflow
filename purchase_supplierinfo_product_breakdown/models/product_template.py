from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    use_product_components = fields.Boolean()
