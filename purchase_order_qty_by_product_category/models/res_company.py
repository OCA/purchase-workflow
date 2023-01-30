# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    po_category_qty_split_by_uom = fields.Boolean()
    po_category_qty_split_by_uom_reference = fields.Boolean()
