# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderManualReceiptLine(models.TransientModel):
    _inherit = "purchase.order.manual.receipt.wizard.line"

    def _get_move_vals_list(self):
        # OVERRIDE: we'll split the purchase line here, assign the new line
        # to field `purchase_line_id`, and then call the `super` so that method
        # `_get_move_vals()` will read data from the new split line instead
        # of the original line
        self._split_purchase_line()
        return super()._get_move_vals_list()

    def _split_purchase_line(self):
        """Splits purchase line in a new line"""
        # Assign the new line to the wizard
        for line in self:
            line.purchase_line_id = line.purchase_line_id._split_purchase_line(
                line._get_split_purchase_line_vals()
            )

    def _get_split_purchase_line_vals(self) -> dict:
        """Returns values to be assigned to the new split PO line"""
        self.ensure_one()
        return {
            "manually_split_from_line_id": self.purchase_line_id.id,
            "product_qty": self.qty,
            "product_uom": self.uom_id.id,
            "price_unit": self.unit_price,
            "date_planned": self.wizard_id.scheduled_date,
        }
