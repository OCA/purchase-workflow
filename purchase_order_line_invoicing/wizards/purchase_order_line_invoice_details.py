# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLineInvoiceDetails(models.TransientModel):
    _name = "purchase.order.line.invoice.details"
    _description = "Purchase Order Line Invoice Wizard Details"

    wizard_id = fields.Many2one(
        comodel_name="purchase.order.line.invoice.wizard",
        required=True,
        ondelete="cascade",
    )
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line", ondelete="cascade", required=True
    )
    order_id = fields.Many2one(related="purchase_order_line_id.order_id", readonly=True)
    product_id = fields.Many2one(
        related="purchase_order_line_id.product_id", readonly=True
    )
    name = fields.Text(related="purchase_order_line_id.name", readonly=True)
    product_qty = fields.Float(
        related="purchase_order_line_id.product_qty", readonly=True
    )
    price_unit = fields.Float(
        related="purchase_order_line_id.price_unit", readonly=True
    )
    price_subtotal = fields.Monetary(
        related="purchase_order_line_id.price_subtotal", readonly=True
    )
    currency_id = fields.Many2one(
        related="purchase_order_line_id.currency_id", readonly=True
    )
    qty_invoiced = fields.Float(
        related="purchase_order_line_id.qty_to_invoice", readonly=True
    )
    qty_received = fields.Float(
        related="purchase_order_line_id.qty_received", readonly=True
    )
    invoice_qty = fields.Float("Quantity to Invoice", required=True)
