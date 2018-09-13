# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockWharehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        # Allow change search purchase requisition domain only when
        # grouped_by_type is in context
        my_ctx = self.with_context(grouped_by_type=True)
        return super(StockWharehouseOrderpoint, my_ctx)._quantity_in_progress()
