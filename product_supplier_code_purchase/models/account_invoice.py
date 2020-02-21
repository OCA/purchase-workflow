# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_supplier_code = fields.Char(
        string="Product Supplier Code", related="purchase_line_id.product_supplier_code"
    )
