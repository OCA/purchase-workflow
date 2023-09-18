# Copyright 2021 Ametras
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    product_uom_po_id = fields.Many2one(
        "uom.uom",
        related="product_id.uom_po_id",
        readonly=True,
    )
