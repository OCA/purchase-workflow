# Copyright 2023 Sygel - Ángel García de la Chica Herrera
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_supplier_discount_real = fields.Boolean(
        string="Real Purchase Supplier Discount", default=False
    )
