# Copyright 2023 Moduon Team
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    invoice_status = fields.Selection(
        related="order_id.invoice_status",
        readonly=True,
        store=True,
        index=True,
    )
    date_order = fields.Datetime(
        store=True,
        index=True,
    )
