# Copyright 2024 Raumschmiede GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import fields, models
from odoo.tools import float_is_zero, groupby

METHOD_RECEPTION = "reception"


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_received_method = fields.Selection(
        selection_add=[(METHOD_RECEPTION, "Reception")]
    )

    def _is_received_method_reception(self):
        self.ensure_one()

        return (
            self.product_id.type == "service"
            and self.product_id.purchase_method == "receive"
        )

    def _compute_qty_received_method(self):
        super()._compute_qty_received_method()

        for line in self:
            if line._is_received_method_reception():
                line.qty_received_method = METHOD_RECEPTION

    def _get_reception_qty_received(self, received):
        self.ensure_one()

        if received:
            return self.product_uom_qty

        return 0.0

    def _compute_qty_received_reception_method(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        # When picking is set to done, in self are only the lines that have a stock
        # move connected. So take all lines of self's PO to be sure to set qty_received
        # for the service products
        lines_grouped = groupby(
            self.order_id.order_line.filtered(
                lambda line: line.qty_received_method == METHOD_RECEPTION
            ),
            lambda l: l.order_id,
        )
        for order, lines in lines_grouped:
            # True if at least one PO line with a stock product has a qty_received set.
            # When qty_received is manually set on a line with a service product with
            # another purchase_method, this does not affect reception service products
            received = any(
                line.qty_received_method == "stock_moves"
                and not float_is_zero(line.qty_received, precision)
                for line in order.order_line
            )
            for line in lines:
                # If any non-service PO line has a received qty or all of them have no
                # stock moves, all reception service lines of a PO are received
                line.qty_received = line._get_reception_qty_received(received)

    # This method is not triggered for service line products as they do not have stock
    # moves as the stock products when the picking is set to done
    def _compute_qty_received(self):
        super()._compute_qty_received()
        self._compute_qty_received_reception_method()
