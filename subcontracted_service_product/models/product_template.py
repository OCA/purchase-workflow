# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subcontracted_product_id = fields.Many2one(
        related="product_variant_ids.subcontracted_product_id",
        comodel_name="product.product",
        string="Will subcontract this service",
        domain="[('type', '=', 'service')]",
        required=False,
    )
