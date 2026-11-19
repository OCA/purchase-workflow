# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("order_id.force_invoiced")
    def _compute_qty_invoiced(self):
        """Reset qty_to_invoice as per order force invoiced"""
        res = super()._compute_qty_invoiced()
        self.filtered(
            lambda pol: pol.order_id.force_invoiced and pol.qty_to_invoice
        ).qty_to_invoice = 0
        return res
