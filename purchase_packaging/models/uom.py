# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UoMCategory(models.Model):
    _inherit = "uom.category"
    _description = "Product UoM Categories"

    uom_ids = fields.One2many(comodel_name="uom.uom", inverse_name="category_id")
    reference_uom_id = fields.Many2one(
        comodel_name="uom.uom", compute="_compute_reference_uom_id"
    )

    def _compute_reference_uom_id(self):
        for category in self:
            category.reference_uom_id = category.uom_ids.filtered(
                lambda u: u.uom_type == "reference"
            )
