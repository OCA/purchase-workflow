# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def update_lines_info(self):
        self.ensure_one()
        for line in self.order_line:
            line._compute_price_unit_and_date_planned_and_name()
        return True
