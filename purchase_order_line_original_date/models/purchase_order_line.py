# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    original_date_planned = fields.Datetime(
        string="Original Delivery Date",
        readonly=True,
        copy=False,
        help="Original delivery date at PO confirmation.",
    )
