# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            requisition = order.requisition_id
            if order.requisition_id and requisition.from_rfq:
                order._auto_cancel_another_order()
                requisition.vendor_id = order.partner_id.id
                for line in requisition.line_ids:
                    price_unit = order.order_line.filtered(
                        lambda l: l.product_id == line.product_id)\
                        .mapped('price_unit')
                    if price_unit:
                        line.price_unit = max(price_unit)
        return res

    def _auto_cancel_another_order(self):
        requisition_id = self.requisition_id.id
        purchases = self.env['purchase.order'].search(
            [('requisition_id', '=', requisition_id)])
        for purchase in purchases:
            if purchase.state != 'purchase':
                purchase.state = 'cancel'
