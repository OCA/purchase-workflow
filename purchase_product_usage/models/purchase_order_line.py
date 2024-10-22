# Copyright 2019 Aleph Objects, Inc.
# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    usage_id = fields.Many2one(comodel_name="purchase.product.usage", string="Usage")

    @api.onchange("usage_id")
    def onchange_usage_id(self):
        if self.usage_id.product_id and not self.product_id:
            self.product_id = self.usage_id.product_id
