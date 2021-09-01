# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.product"

    default_packaging = fields.Many2one(
        comodel_name="product.packaging", string="Default Product Packaging",
    )
