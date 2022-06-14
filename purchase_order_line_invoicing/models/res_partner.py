# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_order_lines_count = fields.Float(
        compute="_compute_purchase_order_lines_count"
    )

    def _compute_purchase_order_lines_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search(
            [("id", "child_of", self.ids)]
        )
        all_partners.read(["parent_id"])

        purchase_order_line_groups = self.env["purchase.order.line"].read_group(
            domain=[("partner_id", "in", all_partners.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )
        partners = self.browse()
        for group in purchase_order_line_groups:
            partner = self.browse(group["partner_id"][0])
            while partner:
                if partner in self:
                    partner.purchase_order_lines_count += group["partner_id_count"]
                    partners |= partner
                partner = partner.parent_id
        (self - partners).purchase_order_lines_count = 0
