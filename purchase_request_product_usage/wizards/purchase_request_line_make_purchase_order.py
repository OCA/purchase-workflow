# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).


from odoo import api, fields, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _get_order_line_search_domain(self, order, item):
        order_line_data = super(
            PurchaseRequestLineMakePurchaseOrder,
            self)._get_order_line_search_domain(order, item)
        if item.line_id.usage_id:
            order_line_data.append(
                ('usage_id', '=', item.line_id.usage_id.id))
        return order_line_data

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).\
            _prepare_purchase_order_line(po, item)
        res.update(usage_id=item.usage_id.id)
        return res

    @api.model
    def _prepare_item(self, line):
        res = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_item(
            line)
        res.update(usage_id=line.usage_id.id)
        return res


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order.item"

    usage_id = fields.Many2one(
        comodel_name='purchase.product.usage',
        related='line_id.usage_id',
        string="Usage")
