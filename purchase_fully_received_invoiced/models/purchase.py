# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # This field is more complete than the standard is_shipped
    is_fully_shipped = fields.Boolean(
        compute="_compute_is_fully_shipped", store=True, index=True
    )
    # Same as invoice_status, but excluding invoices in draft
    invoice_status_validated = fields.Selection(
        [
            ("no", "Nothing to Bill"),
            ("to invoice", "Waiting Bills"),
            ("invoiced", "Fully Billed"),
        ],
        string="Posted Billing Status",
        compute="_compute_invoice_status_validated",
        store=True,
        readonly=True,
        copy=False,
        default="no",
    )

    @api.depends("order_line.qty_received")
    def _compute_is_fully_shipped(self):
        for purchase in self:
            if all(
                line.product_qty <= line.qty_received for line in purchase.order_line
            ):
                purchase.is_fully_shipped = True
            else:
                purchase.is_fully_shipped = False

    @api.depends("invoice_status")
    def _compute_invoice_status_validated(self):
        # Same as invoice status, execpt it is not invoiced unless there is no invoice
        # in draft
        for order in self:
            if order.invoice_status in ("no", "to invoice"):
                order.invoice_status_validated = order.invoice_status
            else:
                if not any(inv.state == "draft" for inv in order.invoice_ids):
                    order.invoice_status_validated = order.invoice_status
                else:
                    order.invoice_status_validated = "to invoice"
