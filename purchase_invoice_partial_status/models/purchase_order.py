# Copyright 2025 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Adding a new invoice status option for partial invoicing
    invoice_status = fields.Selection(
        selection_add=[("partially_invoiced", "Partially Invoiced")]
    )

    @api.depends(
        "state",
        "order_line.qty_invoiced",
        "order_line.qty_received",
        "order_line.product_qty",
    )
    def _get_invoiced(self):
        res = super()._get_invoiced()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        for order in self:
            if order.state in ("purchase", "done"):
                total_qty = sum(
                    order.order_line.filtered(lambda l: not l.display_type).mapped(
                        "product_qty"
                    )
                )
                invoiced_qty = sum(
                    order.order_line.filtered(lambda l: not l.display_type).mapped(
                        "qty_invoiced"
                    )
                )
                received_qty = sum(
                    order.order_line.filtered(lambda l: not l.display_type).mapped(
                        "qty_received"
                    )
                )

                if (
                    not float_is_zero(invoiced_qty, precision_digits=precision)
                    and invoiced_qty < total_qty
                    and received_qty > 0
                ):
                    order.invoice_status = "partially_invoiced"
        return res
