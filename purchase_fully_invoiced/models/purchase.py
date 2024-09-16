# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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

    @api.depends("invoice_status", "invoice_ids.state")
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
