# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_qty_pre_split = fields.Float(
        digits="Product Unit of Measure",
        string="Pre-split Original Qty",
        readonly=True,
    )
    manually_split_from_line_id = fields.Many2one(
        "purchase.order.line",
        ondelete="restrict",
        readonly=True,
    )
    manually_split_into_line_ids = fields.One2many(
        "purchase.order.line",
        "manually_split_from_line_id",
        readonly=True,
    )

    def _unlink_except_purchase_or_done(self):
        # OVERRIDE: this method is originally decorated with `api.ondelete()`,
        # which makes Odoo trigger this method whenever a line is deleted, and
        # will raise an error if the line's order is either 'done' or
        # 'purchase'. However, this will make it impossible to merge PO lines
        # when a manual picking is cancelled.
        # While merging the split line into its original line, adding
        # the `manually_split` flag will make sure everything will work
        # correctly.
        lines = self.filtered(lambda x: x.order_id.receipt_expectation != "manual")
        return super(PurchaseOrderLine, lines)._unlink_except_purchase_or_done()

    def _create_or_update_picking(self):
        # OVERRIDE: the `purchase_stock` module introduces this method that
        # is called whenever a PO line is created in a confirmed order, or
        # when line's qty is changed in a confirmed order. This means that
        # splitting a PO line from the wizard will call this method, that will
        # create or update a picking which is not the one we're creating from
        # the manual wizard. As a result, we'll find ourselves with unwanted
        # data (a stock move qty might be changed, a new picking might be
        # created, etc).
        # While copying the old PO line to create the split line, adding
        # the `manually_split` flag will make sure everything will work
        # correctly.
        lines = self.filtered(lambda x: x.order_id.receipt_expectation != "manual")
        return super(PurchaseOrderLine, lines)._create_or_update_picking()

    @api.depends("manually_split_from_line_id")
    def _compute_feasible_for_manual_receipt(self):
        # OVERRIDE: original line is feasible if delivery method is via stock
        # moves; here, we'll also add the condition that the line should not
        # have been split from another line
        split = self.filtered("manually_split_from_line_id")
        split.feasible_for_manual_receipt = False
        return super(
            PurchaseOrderLine, self - split
        )._compute_feasible_for_manual_receipt()

    def _split_purchase_line(self, copy_vals=None):
        """Splits purchase line in a new line"""
        self.ensure_one()
        copy_vals = dict(copy_vals or [])
        # Before splitting: if the line has never been split before, set its
        # current ordered qty as "pre-split qty"
        if not self.manually_split_into_line_ids:
            self.product_qty_pre_split = self.product_qty
        # Copy the original line to a new line with wizard line data
        new = self.copy(copy_vals)
        # Remove the new line's qty from the original line's qty
        to_remove = new.product_uom._compute_quantity(new.product_qty, self.product_uom)
        self.product_qty = max(0, self.product_qty - to_remove)
        return new

    def _merge_back_into_original_line(self, quantity):
        """Reverts quantity from split lines to their origin lines"""
        if not self.manually_split_from_line_id:
            return
        self.ensure_one()
        origin = self.manually_split_from_line_id
        origin.product_qty += self.product_uom._compute_quantity(
            quantity, origin.product_uom
        )
        self.product_qty -= quantity
        # Remove empty lines with no done moves attached
        if float_is_zero(
            self.product_qty, precision_rounding=self.product_uom.rounding
        ) and not any(move.state == "done" for move in self.move_ids):
            self.unlink()
