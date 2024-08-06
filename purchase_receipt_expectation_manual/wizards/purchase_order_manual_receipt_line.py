# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderManualReceiptLine(models.TransientModel):
    _name = "purchase.order.manual.receipt.wizard.line"
    _description = "PO Manual Receipt Wizard Line"

    wizard_id = fields.Many2one(
        "purchase.order.manual.receipt.wizard",
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="purchase_line_id.currency_id",
        readonly=True,
    )

    product_id = fields.Many2one(
        "product.product",
        related="purchase_line_id.product_id",
        readonly=True,
        store=True,
    )

    purchase_line_id = fields.Many2one(
        "purchase.order.line",
        ondelete="cascade",
        required=True,
    )

    purchase_order_id = fields.Many2one(
        "purchase.order",
        related="wizard_id.purchase_order_id",
        store=True,
    )

    qty = fields.Float(
        digits="Product Unit of Measure",
        string="Quantity",
    )

    uom_category_id = fields.Many2one(
        "uom.category",
        related="product_id.uom_id.category_id",
        store=True,
    )

    uom_id = fields.Many2one(
        "uom.uom",
        ondelete="cascade",
        required=True,
        string="Unit of Measure",
    )

    unit_price = fields.Monetary(
        required=True,
    )

    @api.onchange("purchase_line_id")
    def _onchange_purchase_line_id(self):
        po_line = self.purchase_line_id
        if po_line:
            wizlines = self.wizard_id.line_ids
            vals = po_line._prepare_manual_receipt_wizard_line_vals(wizlines)
            self.update(vals)

    def _get_move_vals_list(self) -> list:
        """Returns list of `stock.move.create()` values"""
        return [line._get_move_vals() for line in self]

    def _get_move_vals(self) -> dict:
        """Returns `stock.move.create()` values"""
        self.ensure_one()
        # Use `purchase.order.line` utilities to create picking data properly,
        # then just update the picking values according to wizard line
        vals = self.purchase_line_id._prepare_stock_move_vals(
            self.env["stock.picking"], self.unit_price, self.qty, self.uom_id
        )
        # Picking will be assigned by wizard's `_generate_picking()` method
        vals.pop("picking_id", False)
        vals["manually_generated"] = True
        return vals
