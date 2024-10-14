# Copyright 2024 ForgeFlow (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    reception_status = fields.Selection(
        [
            ("no", "Nothing Received"),
            ("partial", "Partially Received"),
            ("received", "Fully Received"),
        ],
        compute="_compute_reception_status",
        store=True,
    )
    force_received = fields.Boolean(
        readonly=False,
        states={"draft": [("readonly", True)]},
        compute="_compute_force_received",
        store=True,
        copy=False,
        help="If true, the reception status will be forced to Fully Received, "
        "even if some quantities are not fully received. ",
    )

    @api.depends("order_id.force_received")
    def _compute_force_received(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for rec in self:
            if (
                rec.order_id.force_received
                and not float_compare(
                    rec.qty_received, rec.product_qty, precision_digits=prec
                )
                >= 0
            ):
                rec.force_received = True

    @api.depends(
        "state",
        "force_received",
        "qty_received",
        "product_qty",
        "order_id.force_received",
    )
    def _compute_reception_status(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for line in self:
            status = "no"
            if line.order_id.state in ("purchase", "done"):
                if line.force_received:
                    status = "received"
                elif (
                    float_compare(
                        line.qty_received, line.product_qty, precision_digits=prec
                    )
                    >= 0
                ):
                    status = "received"
                elif float_compare(line.qty_received, 0, precision_digits=prec) > 0:
                    status = "partial"
            line.reception_status = (
                status if not line.order_id.force_received else "received"
            )
