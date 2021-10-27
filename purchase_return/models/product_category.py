# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models

from odoo.addons.account.models.product import ACCOUNT_DOMAIN


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_account_vendor_return_categ_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Purchase Returns Account",
        domain=ACCOUNT_DOMAIN,
        help="Keep this field empty to use the default value from the product category.",
    )
