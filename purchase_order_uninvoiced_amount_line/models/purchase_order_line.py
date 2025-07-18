# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "product_qty",
        "qty_invoiced",
        "qty_received",
        "product_id",
        "product_uom",
        "price_unit",
        "price_subtotal",
    )
    def _compute_amount_uninvoiced(self):
        for line in self:
            if line.product_id.purchase_method == "purchase":
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            price_unit = (
                line.price_subtotal / line.product_qty
                if line.product_qty
                else line.price_unit
            )
            amount_uninvoiced = max(0, qty * price_unit)
            line.amount_uninvoiced = line.currency_id.round(amount_uninvoiced)

    amount_uninvoiced = fields.Monetary(
        string="Uninvoiced Amount",
        readonly=True,
        compute="_compute_amount_uninvoiced",
        store=True,
        currency_field="currency_id",
    )
