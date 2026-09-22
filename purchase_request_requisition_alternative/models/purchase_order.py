# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("alternative_po_ids"):
            for order in self:
                order._link_purchase_requests_to(order.alternative_po_ids)
        return res

    def _link_purchase_requests_to(self, orders):
        """Point the purchase requests behind ``self`` at ``orders`` too.

        A purchase request line keeps the purchase order lines it ended up
        on, and derives its purchased quantity from them. When an RFQ gains
        an alternative, the request has to reach the alternative as well,
        otherwise opening the request from there leads nowhere.

        Lines are paired by product: linking a request line to alternative
        lines of other products would inflate the quantity it believes has
        been purchased.
        """
        self.ensure_one()
        targets = orders.order_line
        if not targets:
            return
        request_lines = self.env["purchase.request.line"].search(
            [("purchase_lines", "in", self.order_line.ids)]
        )
        for request_line in request_lines:
            product = request_line.product_id
            matching = targets.filtered(lambda line, p=product: line.product_id == p)
            to_link = matching - request_line.purchase_lines
            if to_link:
                request_line.purchase_lines = [
                    Command.link(line.id) for line in to_link
                ]
