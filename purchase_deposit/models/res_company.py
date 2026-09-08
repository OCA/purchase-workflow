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
    purchase_deposit_limit_order_total = fields.Boolean(
        string="Limit Deposits to Order Total",
        help="Refuse a deposit when the deposits already invoiced, plus the "
        "one being registered, exceed the purchase order total.",
    )
