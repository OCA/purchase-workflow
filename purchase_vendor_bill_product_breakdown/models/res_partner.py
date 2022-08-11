from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    bill_components = fields.Boolean(string="Use Vendor Bill Breakdown")
