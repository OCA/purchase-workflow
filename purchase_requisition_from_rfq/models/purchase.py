# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            requisition = order.requisition_id
            if requisition and requisition.from_rfq:
                order._auto_cancel_another_order()
                requisition.vendor_id = order.partner_id.id
                for line in requisition.line_ids:
                    price_unit = order.order_line.filtered(
                        lambda l: l.product_id == line.product_id
                    ).mapped("price_unit")
                    if price_unit:
                        line.price_unit = max(price_unit)
        return res

    def _auto_cancel_another_order(self):
        self.ensure_one()
        purchases = self.search([("requisition_id", "=", self.requisition_id.id)])
        purchases.filtered(lambda l: l.state != "purchase").state = "cancel"
