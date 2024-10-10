# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    pending_to_receive = fields.Boolean(compute="_compute_pending_to_receive")

    def _compute_pending_to_receive(self):
        for order in self:
            order.pending_to_receive = True
            if all(
                val is False
                for val in order.mapped("order_line.pending_to_receive")
            ):
                order.pending_to_receive = False

    @api.multi
    def button_confirm_manual(self):
        super(
            PurchaseOrder, self.with_context(manual_delivery=True)
        ).button_confirm()

    @api.multi
    def _create_picking(self):
        if self.env.context.get("manual_delivery", False):
            # We do not want to create the picking when confirming the order
            # if it comes from manual confirmation
            return
        return super()._create_picking()


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    existing_qty = fields.Float(
        compute="_compute_existing_qty",
        string="Existing Qty",
        digits=dp.get_precision("Product Unit of Measure"),
        help="Quantity already planned or shipped (stock movements "
        "already created)",
    )
    pending_to_receive = fields.Boolean(
        compute="_compute_existing_qty",
        store=True,
        string="Pending Qty to Receive",
        help="There is pending quantity to receive not yet planned",
    )

    @api.depends(
        "move_ids",
        "move_ids.state",
        "move_ids.location_id",
        "move_ids.location_dest_id",
    )
    def _compute_existing_qty(self):
        for line in self:
            rounding = line.company_id.currency_id.rounding
            total = 0.0
            for move in line.move_ids:
                if move.state not in ["cancel"]:
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(
                                move.product_uom_qty, line.product_uom
                            )
                    elif (
                        move.origin_returned_move_id._is_dropshipped()
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
                            move.product_uom_qty, line.product_uom
                        )
            line.existing_qty = total
            if float_compare(
                line.product_uom_qty,
                line.existing_qty,
                precision_rounding=rounding,
            ):
                line.pending_to_receive = True
            else:
                line.pending_to_receive = False
