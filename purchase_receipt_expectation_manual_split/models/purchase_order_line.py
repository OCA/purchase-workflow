# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_qty_pre_split = fields.Float(
        digits="Product Unit of Measure",
        string="Pre-split Original Qty",
    )

    manually_split_from_line_id = fields.Many2one(
        "purchase.order.line",
        ondelete="restrict",
    )

    manually_split_into_line_ids = fields.One2many(
        "purchase.order.line",
        "manually_split_from_line_id",
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
        orig = self.with_context(skip_picking_create=True)
        new = orig.copy(copy_vals)
        # Remove the new line's qty from the original line's qty
        to_remove = new.product_uom._compute_quantity(new.product_qty, orig.product_uom)
        orig.product_qty = max(0, orig.product_qty - to_remove)
        return new

    def _merge_back_into_original_lines(self):
        """Reverts quantity from split lines to their origin lines"""
        to_merge = self.filtered("manually_split_from_line_id")
        if to_merge:
            to_merge = to_merge.with_context(
                # Skip picking update when original line qty is updated
                skip_picking_create=True,
                # Skip order check when lines are deleted post-merge
                skip_order_state_check=True,
            )
            split_map = {
                orig: orig.manually_split_into_line_ids
                for orig in to_merge.manually_split_from_line_id
            }
            for orig, lines in split_map.items():
                lines_to_merge = lines & to_merge
                if lines_to_merge == lines:
                    # Shortcut: we're deleting every split lines, so we'll
                    # simply revert the original qty without going through
                    # the `for` cycle
                    orig.product_qty = orig.product_qty_pre_split
                    continue
                for line in lines_to_merge:
                    from_uom = line.product_uom
                    qty = line.product_qty
                    to_uom = orig.product_uom
                    orig.product_qty += from_uom._compute_quantity(qty, to_uom)
            to_merge.unlink()
