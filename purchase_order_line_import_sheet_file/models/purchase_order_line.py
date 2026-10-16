# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def action_open_line_import(self):
        order = self.env["purchase.order"].browse(self.env.context.get("order_id"))
        return order.action_open_line_import()
