# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "stock.picking"

    def action_cancel(self):
        self.move_lines.purchase_line_id._merge_back_into_original_lines()
        return super().action_cancel()
