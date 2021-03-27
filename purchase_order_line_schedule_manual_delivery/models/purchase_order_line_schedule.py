# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools import float_compare

from odoo.addons import decimal_precision as dp


class PurchaseOrderLineSchedule(models.Model):
    _inherit = "purchase.order.line.schedule"

    qty_in_receipt = fields.Float(
        compute="_compute_qty_in_receipt",
        string="In Receipt",
        compute_sudo=True,
        digits=dp.get_precision("Product Unit of Measure"),
        help="Quantity already in an incoming shipment pending to receive",
    )
    pending_to_receive = fields.Boolean(
        compute="_compute_qty_in_receipt",
        compute_sudo=True,
        string="Pending to Receive",
        help="There is pending quantity to receive not yet planned",
    )

    def _compute_qty_in_receipt(self):
        for rec in self:
            rec.qty_in_receipt = 0.0
            rec.pending_to_receive = False
        for ol in self.mapped("order_line_id"):
            for sl in ol.schedule_line_ids:
                sl.qty_in_receipt = 0.0
                sl.pending_to_receive = False
            rounding = ol.company_id.currency_id.rounding

            for move in ol.move_ids.filtered(
                lambda m: m.product_id == ol.product_id
                and m.state not in ("done", "cancel")
            ).sorted(lambda ml: ml.date_expected):
                total = 0.0

                if move.location_dest_id.usage == "supplier":
                    if move.to_refund:
                        total -= move.product_uom._compute_quantity(
                            move.product_uom_qty, ol.product_uom
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
                        move.product_uom_qty, ol.product_uom
                    )
                to_allocate = total
                # Try to allocate first to the schedule lines that match
                # exactly in the date
                for sl in ol.schedule_line_ids.filtered(
                    lambda l: l.date_planned.date() == move.date_expected.date()
                ):
                    qty = min(to_allocate, sl.product_qty - sl.qty_received)
                    sl.qty_in_receipt += qty
                    to_allocate -= qty
                # Now try to allocate the remaining qty
                for sl in ol.schedule_line_ids.sorted(lambda l: l.date_planned):
                    qty = min(to_allocate, sl.product_qty - sl.qty_received)
                    sl.qty_in_receipt += qty
                    to_allocate -= qty
            for sl in ol.schedule_line_ids:
                if float_compare(
                    sl.product_qty, sl.qty_in_receipt, precision_rounding=rounding,
                ):
                    sl.pending_to_receive = True
                else:
                    sl.pending_to_receive = False
