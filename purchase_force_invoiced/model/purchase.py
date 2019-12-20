# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_invoiced = fields.Boolean(
        string="Force invoiced",
        readonly=True,
        states={"done": [("readonly", False)]},
        copy=False,
        help="When you set this field, the purchase order will be "
        "considered as fully billed, even when there may be ordered "
        "or delivered quantities pending to bill.",
    )

    @api.depends("force_invoiced")
    def _get_invoiced(self):
        super(PurchaseOrder, self)._get_invoiced()
        for order in self.filtered(
            lambda po: po.force_invoiced and po.invoice_status == "to invoice"
        ):
            order.invoice_status = "invoiced"


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_account_move_line(self, line):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(line)
        if res.get("purchase_line_id", False):
            pol = self.browse(res["purchase_line_id"])
            if pol.order_id.force_invoiced:
                res["quantity"] = 0.0
        return res
