# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_invoiced = fields.Boolean(
        copy=False,
        tracking=True,
        help="When you set this field, the purchase order will be "
        "considered as fully billed, even when there may be ordered "
        "or delivered quantities pending to bill. To use this field, "
        "the order must be in 'Locked' state",
    )

    @api.depends("force_invoiced")
    def _get_invoiced(self):
        res = super()._get_invoiced()
        for order in self.filtered(
            lambda po: po.force_invoiced and po.invoice_status == "to invoice"
        ):
            order.invoice_status = "invoiced"
        return res

    def action_create_invoice(self, attachment_ids=False):
        orders_to_invoice = self.env["purchase.order"]
        for order in self:
            if not order.force_invoiced:
                orders_to_invoice |= order
        if not orders_to_invoice:
            return {"type": "ir.actions.act_window_close"}
        return super(PurchaseOrder, orders_to_invoice).action_create_invoice(
            attachment_ids=attachment_ids
        )
