# Copyright 2020 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_item(self, line):
        res = super()._prepare_item(line)
        if line.secondary_uom_id:
            res.update({
                'secondary_uom_qty': line.secondary_uom_qty,
                'secondary_uom_id': line.secondary_uom_id.id,
            })
        return res

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        res = super()._prepare_purchase_order_line(po, item)
        if item.line_id.secondary_uom_id:
            res.update({
                'secondary_uom_qty': item.line_id.secondary_uom_qty,
                'secondary_uom_id': item.line_id.secondary_uom_id.id,
            })
        return res


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order.item"

    secondary_uom_qty = fields.Float(
        string='Secondary Qty',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Secondary uom',
        ondelete='restrict',
    )
