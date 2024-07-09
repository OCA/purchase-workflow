# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    type = fields.Selection(
        selection_add=[("distribution", "Distribution")],
        ondelete={"distribution": "set default"},
    )
