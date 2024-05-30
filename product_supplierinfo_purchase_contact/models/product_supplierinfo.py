# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    purchase_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Purchase contact"
    )
