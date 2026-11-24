# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "product_qty",
        "qty_received",
        "qty_invoiced",
        "price_subtotal",
        "force_invoiced",
        "invoice_status",
    )
    def _compute_amount_uninvoiced(self):
        super()._compute_amount_uninvoiced()
        for line in self:
            if line.force_invoiced or line.invoice_status == "invoiced":
                line.amount_uninvoiced = 0.0
            else:
                # Ensure invoiced + uninvoiced = ordered
                # (ignore qty_received to avoid "limbo" amounts)
                qty = line.product_qty - line.qty_invoiced
                price_unit = (
                    line.price_subtotal / line.product_qty
                    if line.product_qty
                    else line.price_unit
                )
                amount_uninvoiced = max(0, qty * price_unit)
                line.amount_uninvoiced = line.currency_id.round(amount_uninvoiced)
        return True
