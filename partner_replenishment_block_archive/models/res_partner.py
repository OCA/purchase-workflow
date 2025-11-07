# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        if "active" in vals and not vals["active"]:
            replenishements = self.env["stock.warehouse.orderpoint"].search(
                [("supplier_id", "in", self.ids)], limit=1
            )
            if replenishements:
                raise ValidationError(
                    _("You cannot archive a partner with replenishement rule.")
                )
        return super().write(vals)
