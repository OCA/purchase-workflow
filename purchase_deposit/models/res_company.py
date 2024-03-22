# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_deposit_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Purchase Deposit Product",
        domain=[("type", "=", "service")],
        help="Default product used for payment advances.",
    )
