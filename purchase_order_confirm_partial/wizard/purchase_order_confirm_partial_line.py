# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class PurchaseOrderConfirmPartialLine(models.TransientModel):
    _name = "purchase.order.confirm.partial.line"
    _description = "Partial RFQ Confirmation Line"

    wizard_id = fields.Many2one(
        comodel_name="purchase.order.confirm.partial",
        required=True,
    )
    po_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Order Line",
        domain="[('order_id', '=', parent.purchase_order_id)]",
        required=True,
    )
    confirmed_qty = fields.Float(
        string="Confirmed Quantity",
        compute="_compute_confirmed_qty",
        readonly=False,
        required=True,
        store=True,
    )

    @api.constrains("confirmed_qty", "po_line_id")
    def _check_confirmed_qty(self):
        for line in self:
            if line.confirmed_qty < 0:
                raise exceptions.ValidationError(
                    _("Confirmed quantity cannot be negative.")
                )
            if line.confirmed_qty > line.po_line_id.product_qty:
                raise exceptions.ValidationError(
                    _("Confirmed quantity cannot be greater than ordered quantity.")
                )

    @api.depends("po_line_id")
    def _compute_confirmed_qty(self):
        for line in self:
            line.confirmed_qty = line.po_line_id.product_qty
