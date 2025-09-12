# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoice_status = fields.Selection(
        selection=[
            ("no", "Nothing to Bill"),
            ("to invoice", "Waiting Bills"),
            ("invoiced", "Fully Billed"),
        ],
        compute="_compute_invoice_status",
        store=True,
        related=False,
        string="Billing Status",
    )

    force_invoiced = fields.Boolean(
        store=True,
        copy=False,
        help="If true, the invoice status will be forced to Fully Invoiced, "
        "even if some quantities are not fully invoiced. ",
    )

    @api.depends("qty_invoiced", "product_qty", "force_invoiced")
    def _compute_invoice_status(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for line in self:
            if line.order_id.state not in ["purchase", "done"]:
                line.invoice_status = "no"
                continue
            if line.display_type:
                line.invoice_status = False
                continue
            if line.force_invoiced:
                line.invoice_status = "invoiced"
                continue
            if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                if line.qty_invoiced >= line.product_qty:
                    line.invoice_status = "invoiced"
                else:
                    line.invoice_status = "no"
            else:
                line.invoice_status = "to invoice"
