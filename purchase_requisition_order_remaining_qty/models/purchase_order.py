# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange("requisition_id")
    def _onchange_requisition_id(self):
        """In this function the lines are added to the order. At the end we will
        auto-delete the lines with quantity 0."""
        super()._onchange_requisition_id()
        self.order_line -= self.order_line.filtered(lambda x: x.product_qty == 0)
