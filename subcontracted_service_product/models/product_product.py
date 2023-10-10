# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    subcontracted_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Will subcontract this service product",
    )
