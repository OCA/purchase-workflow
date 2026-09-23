# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    source_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Vendor Location",
        compute="_compute_location_id",
    )

    @api.depends("partner_id")
    def _compute_location_id(self):
        for order in self:
            order.source_location_id = order.partner_id.property_stock_supplier

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res["location_id"] = self.source_location_id.id
        return res
