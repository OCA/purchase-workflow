# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def set_last_price_info(cr, registry):
    """
    This post-init-hook will update last price information for all products
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())
    product_obj = env["product.product"]
    products = product_obj.search([("purchase_ok", "=", True)])
    products.set_product_last_purchase()
