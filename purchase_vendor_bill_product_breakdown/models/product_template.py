from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bill_components = fields.Boolean(string="Use Vendor Bill Breakdown")
