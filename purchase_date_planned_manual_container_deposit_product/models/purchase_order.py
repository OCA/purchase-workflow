# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def prepare_deposit_container_line(self, product, qty):
        values = super().prepare_deposit_container_line(product, qty)
        if self.date_planned:
            values["date_planned"] = self.date_planned

        return values
