# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_in_receipt = fields.Float(
        compute="_compute_qty_in_receipt",
        store=True,
        digits="Product Unit of Measure",
        help="Quantity for which there are pending stock moves",
    )
    pending_to_receive = fields.Boolean(
        compute="_compute_qty_in_receipt",
        store=True,
        string="Pending Qty to Receive",
        help="There is pending quantity to receive not yet planned",
    )

    @api.depends(
        "move_ids",
        "move_ids.state",
        "move_ids.location_id",
        "move_ids.location_dest_id",
        "product_uom_qty",
        "qty_received",
        "state",
    )
    def _compute_qty_in_receipt(self):
        for line in self:
            precision_digits = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            total = 0.0
            for move in line.move_ids:
                if move.state not in ["cancel", "done"]:
                    if (
                        move.location_id
                        == self.order_id.picking_type_id.default_location_dest_id
                    ):
                        # This is a return to vendor
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(
                                move.quantity, line.product_uom
                            )
                    elif (
                        move.origin_returned_move_id
                        and move.origin_returned_move_id._is_dropshipped()
                        and not move._is_dropshipped_returned()
                    ):
                        # Edge case: the dropship is returned to the stock,
                        # no to the supplier.
                        # In this case, the received quantity on the PO is
                        # set although we didn't receive the product
                        # physically in our stock. To avoid counting the
                        # quantity twice, we do nothing.
                        pass
                    else:
                        total += move.product_uom._compute_quantity(
                            move.quantity, line.product_uom
                        )
            line.qty_in_receipt = total
            if (
                float_compare(
                    line.product_qty,
                    line.qty_in_receipt + line.qty_received,
                    precision_digits=precision_digits,
                )
                == 1
            ):
                line.pending_to_receive = True
            else:
                line.pending_to_receive = False

    def _create_or_update_picking(self):
        # Avoid creating deliveries on manual delivery orders
        if self.env.context.get("ignore_manual_delivery"):
            lines = self
        else:
            lines = self.filtered(lambda pol: not pol.order_id.manual_delivery)
        return super(PurchaseOrderLine, lines)._create_or_update_picking()
