# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    force_invoiced = fields.Float(
        digits="Product Unit of Measure",
        help=(
            "This amount will be deducted from quantity to invoice."
            "\nquantity to invoice = delivered - invoiced - force invoiced"
        ),
    )

    @api.depends("force_invoiced")
    def _compute_qty_invoiced(self):
        """
        Compute the quantity to invoice.
        """
        res = super()._compute_qty_invoiced()
        for line in self.filtered(lambda l: l.force_invoiced):
            # compute qty_to_invoice
            if (
                line.order_id.state in ["purchase", "done"]
                and line.product_id.purchase_method != "purchase"
            ):
                line.qty_to_invoice = (
                    line.qty_received - line.qty_invoiced - line.force_invoiced
                )
        return res
