# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(
        selection_add=[("purchase_invoice", "Purchase invoice address")],
        ondelete={"purchase_invoice": "set null"},
    )
