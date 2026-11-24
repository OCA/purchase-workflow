# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    require_approved_supplier = fields.Boolean(
        string="Require Approved Suppliers",
        default=False,
        help="If checked, products in this category "
        "will require approved suppliers for purchase orders. "
        "This can be overridden at individual product level.",
    )
