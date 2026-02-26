# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderMockUp(models.Model):
    _inherit = "purchase.order"  # pylint: disable=R8180

    receipt_expectation = fields.Selection(
        selection_add=[
            ("succeeding", "Succeeding"),
            ("failing", "Failing"),
        ],
        ondelete={
            "succeeding": "set default",
            "failing": "set default",
        },
    )

    def _create_picking_for_succeeding_receipt_expectation(self):
        """Standard picking creation workflow"""
        orders = self.with_context(skip_custom_receipt_expectation=1)
        return orders._create_picking()
