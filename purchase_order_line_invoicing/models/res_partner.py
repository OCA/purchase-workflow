# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_order_lines_count = fields.Float(
        compute="_compute_purchase_order_lines_count"
    )

    def _compute_purchase_order_lines_count(self):
        purchase_order_line_model = self.env["purchase.order.line"]
        for partner in self:
            domain = [("partner_id", "child_of", partner.id)]
            partner.purchase_order_lines_count = purchase_order_line_model.search_count(
                domain
            )
