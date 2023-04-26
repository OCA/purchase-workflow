# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    po_category_qty_split_by_uom = fields.Boolean(
        related="company_id.po_category_qty_split_by_uom",
        readonly=False,
    )

    po_category_qty_split_by_uom_reference = fields.Boolean(
        related="company_id.po_category_qty_split_by_uom_reference",
        readonly=False,
    )
