# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    is_product_active = fields.Boolean(
        default=True,
        help="Mirrors the active state of the linked product or template. "
        "Stored directly so the 'Active Products' filter needs no SubPlans.",
    )
