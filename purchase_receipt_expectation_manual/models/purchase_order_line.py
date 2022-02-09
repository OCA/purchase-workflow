# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    feasible_for_manual_receipt = fields.Boolean(
        compute="_compute_feasible_for_manual_receipt",
        store=True,
    )

    manually_generated_move_ids = fields.One2many(
        "stock.move",
        "purchase_line_id",
        domain=[("manually_generated", "=", True)],
    )

    manually_receivable_qty = fields.Float(
        compute="_compute_manually_receivable_qty",
        digits="Product Unit of Measure",
        help="Qty that has yet to be received for current line (in product" " PO UoM)",
        store=True,
    )

    manually_receivable_qty_uom = fields.Float(
        compute="_compute_manually_receivable_qty",
        digits="Product Unit of Measure",
        help="Qty that has yet to be received for current line (in line UoM)",
        store=True,
    )

    manually_received_qty = fields.Float(
        compute="_compute_manually_received_qty",
        digits="Product Unit of Measure",
        help="Qty that has been received for current line (in product" " PO UoM)",
        store=True,
    )

    manually_received_qty_uom = fields.Float(
        compute="_compute_manually_received_qty",
        digits="Product Unit of Measure",
        help="Qty that has been received for current line (in product" " PO UoM)",
        store=True,
    )

    @api.depends("qty_received_method")
    def _compute_feasible_for_manual_receipt(self):
        """Computes whether a line can be used in the manual receipt wizard

        By default, True if `qty_received_method` is "stock_moves"
        """
        for line in self:
            line.feasible_for_manual_receipt = line.qty_received_method == "stock_moves"

    @api.depends(
        "manually_generated_move_ids.manually_received_qty",
        "manually_generated_move_ids.state",
        "product_uom",
    )
    def _compute_manually_received_qty(self):
        """Computes qty that has been manually received

        Compute process:
            1- `manually_received_qty` is the sum of manually received
               quantities in related stock moves (this value is already
               measured in product's PO UoM)
            2- `manually_received_qty_uom` is equal to `manually_received_qty`
               converted to line's UoM
        """
        for line in self:
            received = sum(
                m.manually_received_qty
                for m in line.manually_generated_move_ids
                if m.state != "cancel"
            )
            received_uom = 0
            if received:
                # No need to convert anything if `received` is 0
                received_uom = line.product_id.uom_po_id._compute_quantity(
                    received, line.product_uom, round=False
                )
            line.update(
                {
                    "manually_received_qty": received,
                    "manually_received_qty_uom": received_uom,
                }
            )

    @api.depends(
        "feasible_for_manual_receipt",
        "product_uom",
        "product_qty",
        "product_id.uom_po_id",
        "manually_received_qty",
    )
    def _compute_manually_receivable_qty(self):
        """Computes qty that can be manually received

        Compute process:
            1- convert `product_qty` to product PO UoM to have the ordered qty
            2- get received qty from `manually_received_qty` (already in
               product PO UoM)
            3- `manually_receivable_qty` is ordered qty minus received qty; if
               the result is negative, then it is considered as 0
            4- `manually_receivable_qty_uom` is `manually_receivable_qty`
               converted to line's UoM
        """
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for line in self:
            if not line.feasible_for_manual_receipt:
                line.update(
                    {
                        "manually_receivable_qty": 0,
                        "manually_receivable_qty_uom": 0,
                    }
                )
                continue
            # Convert ordered qty from line UoM to product PO UoM to be able to
            # confront it with manually received qty (which is already in
            # product PO UoM)
            ordered = line.product_uom._compute_quantity(
                line.product_qty, line.product_id.uom_po_id, round=False
            )
            received = line.manually_received_qty
            receivable = max(0, float_round(ordered - received, prec))
            receivable_uom = 0
            if receivable:
                # No need to convert anything if `receivable` is 0
                receivable_uom = line.product_id.uom_po_id._compute_quantity(
                    receivable, line.product_uom, round=False
                )
            line.update(
                {
                    "manually_receivable_qty": receivable,
                    "manually_receivable_qty_uom": receivable_uom,
                }
            )

    def _prepare_manual_receipt_wizard_line_vals_list(self) -> list:
        """Returns a list of receipt wizard lines values"""
        vals_list = []
        for line in self.filtered("feasible_for_manual_receipt"):
            vals = line._prepare_manual_receipt_wizard_line_vals()
            if vals:
                vals_list.append(vals)
        return vals_list

    def _prepare_manual_receipt_wizard_line_vals(self, wizlines=None) -> dict:
        """Returns a values for a receipt wizard line

        :param wizlines: existing receipt wizard lines
        """
        self.ensure_one()
        qty = self.manually_receivable_qty
        uom = self.product_uom
        if self.product_id.uom_po_id != uom:
            qty = self.product_id.uom_po_id._compute_quantity(qty, uom, False)

        # If already have wizard lines, remove their qty (this method is called
        # from wizard line's onchange when changing PO line)
        for line in wizlines if wizlines is not None else []:
            if line.purchase_line_id == self:
                qty -= line.uom_id._compute_quantity(line.qty, uom, False)

        # Return an empty dict if qty <= 0 and the method was not called from
        # wizard lines onchange; this way, we won't create a new wizard line
        # when opening a new wizard, but we'll still be able to correctly
        # update a wizard line when the onchange plays (even if it's qty is 0)
        qty = max(qty, 0)
        if not qty and wizlines is None:
            return {}
        return {
            "purchase_line_id": self.id,
            "product_id": self.product_id.id,
            "qty": max(qty, 0),
            "uom_id": uom.id,
            "unit_price": self.price_unit,
        }
