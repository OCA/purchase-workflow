# Copyright 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_order_weight_in_po = fields.Boolean(
        "Display Order Weight in PO",
        default=True,
    )
    display_order_volume_in_po = fields.Boolean(
        "Display Order Volume in PO",
        default=True,
    )
