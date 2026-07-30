# Copyright 2025 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PurchaseOrderReturn(models.Model):
    _inherit = "purchase.return.order"

    @api.onchange("picking_type_id")
    def onchange_picking_type_id(self):
        for line in self.order_line:
            line.onchange_product_id()
