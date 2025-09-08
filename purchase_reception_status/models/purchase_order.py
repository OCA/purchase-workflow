# Copyright 2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    receipt_status = fields.Selection(
        [
            ("pending", "Nothing Received"),
            ("partial", "Partially Received"),
            ("full", "Fully Received"),
        ],
        compute="_compute_oca_receipt_status",
        store=True,
    )
    force_received = fields.Boolean(
        readonly=True,
        copy=False,
        help="If true, the reception status will be forced to Fully Received, "
        "even if some lines are not fully received. "
        "To be able to modify this field, you must first lock the order.",
    )

    @api.depends(
        "state", "force_received", "order_line.qty_received", "order_line.product_qty"
    )
    def _compute_oca_receipt_status(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for order in self:
            status = "pending"
            if order.state in ("purchase", "done"):
                if order.force_received:
                    status = "full"
                elif all(
                    [
                        float_compare(
                            line.qty_received, line.product_qty, precision_digits=prec
                        )
                        >= 0
                        for line in order.order_line
                    ]
                ):
                    status = "full"
                elif any(
                    [
                        float_compare(line.qty_received, 0, precision_digits=prec) > 0
                        for line in order.order_line
                    ]
                ):
                    status = "partial"
            order.receipt_status = status
