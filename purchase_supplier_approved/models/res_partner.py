# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    approved_product_ids = fields.One2many(
        "purchase.supplier.approved",
        "partner_id",
        string="Approved Products",
        help="List of products for which this partner is an approved supplier",
    )
    approved_product_count = fields.Integer(
        string="Approved Products Count",
        compute="_compute_approved_product_count",
    )

    @api.depends("approved_product_ids")
    def _compute_approved_product_count(self):
        for record in self:
            record.approved_product_count = len(record.approved_product_ids)

    def action_view_approved_products(self):
        """Action to view approved products for this supplier"""
        self.ensure_one()
        action = self.env.ref(
            "purchase_supplier_approved.action_purchase_supplier_approved"
        ).read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        action["context"] = {
            "default_partner_id": self.id,
            "search_default_partner_id": self.id,
        }
        if self.approved_product_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.approved_product_ids[0].id
        return action
