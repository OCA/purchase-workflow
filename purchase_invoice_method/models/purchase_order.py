# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_method = fields.Selection(
        lambda r: r.env["product.template"]._fields["purchase_method"].selection
    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "qty_received",
        "product_uom_qty",
        "order_id.state",
        "order_id.invoice_method",
    )
    def _compute_qty_invoiced(self):
        ret = super()._compute_qty_invoiced()
        for line in self.filtered(
            lambda r: r.order_id.invoice_method
            and r.order_id.state in ["purchase", "done"]
        ):
            if line.order_id.invoice_method == "purchase":
                line.qty_to_invoice = line.product_qty - line.qty_invoiced
            elif line.order_id.invoice_method == "receive":
                line.qty_to_invoice = line.qty_received - line.qty_invoiced
        return ret
