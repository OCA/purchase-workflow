# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "mail.thread", "mail.activity.mixin"]

    receipt_status = fields.Selection(
        [
            ("pending", "Nothing Received"),
            ("partial", "Partially Received"),
            ("full", "Fully Received"),
            ("over", "Over Received"),
        ],
        compute="_compute_receipt_status",
        store=True,
    )
    force_received = fields.Boolean(
        store=True,
        copy=False,
        help="If true, the reception status will be forced to Fully Received, "
        "even if some quantities are not fully received. ",
        tracking=True,
    )

    @api.depends(
        "state",
        "force_received",
        "qty_received",
        "product_qty",
    )
    def _compute_receipt_status(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for line in self:
            status = "pending"
            if line.order_id.state in ("purchase", "done"):
                if line.force_received:
                    status = "full"
                else:
                    if (
                        float_compare(
                            line.qty_received, line.product_qty, precision_digits=prec
                        )
                        > 0
                    ):
                        status = "over"
                    elif (
                        float_compare(
                            line.qty_received, line.product_qty, precision_digits=prec
                        )
                        == 0
                    ):
                        status = "full"
                    elif float_compare(line.qty_received, 0, precision_digits=prec) > 0:
                        status = "partial"
            line.receipt_status = status
